"""
Fine-tune the Audita agent with PEFT (LoRA), TRL SFTTrainer, and BitsAndBytes quantization.
Generates a quantized GGUF model for offline inference with llama-cpp-python.

Before running this script, prepare the training data by executing:
    python3 agents/audita/data_prep.py
"""
import subprocess
from pathlib import Path

import pandas as pd
from transformers import LlamaTokenizer, LlamaForCausalLM
import bitsandbytes as bnb
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer, SFTTrainingArguments


def main():
    # Determine repository root
    repo_root = Path(__file__).resolve().parents[2]
    agent_name = 'audita'

    # Dataset paths
    data_dir = repo_root / 'data' / 'training' / agent_name
    df_code = pd.read_parquet(data_dir / 'code.parquet')
    df_config = pd.read_parquet(data_dir / 'configs.parquet')
    records = df_code['content'].tolist() + df_config['content'].tolist()
    train_data = [{'text': t} for t in records]

    # Base model path (local HF format)
    base_model = repo_root / 'ai_models' / 'llms' / 'Wizard-Vicuna-7B'

    # Load tokenizer
    tokenizer = LlamaTokenizer.from_pretrained(base_model)
    tokenizer.padding_side = 'left'
    tokenizer.pad_token_id = tokenizer.eos_token_id

    # Load base model with 4-bit quantization
    model = LlamaForCausalLM.from_pretrained(
        base_model,
        load_in_4bit=True,
        quantization_config=bnb.QuantizationConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type='nf4',
            bnb_4bit_compute_dtype='bfloat16'
        ),
        device_map='auto'
    )
    model = prepare_model_for_kbit_training(model)

    # Configure LoRA
    peft_config = LoraConfig(
        task_type='CAUSAL_LM',
        inference_mode=False,
        r=16,
        lora_alpha=32,
        target_modules=['q_proj', 'v_proj'],
        lora_dropout=0.05,
    )
    model = get_peft_model(model, peft_config)

    # Training arguments
    output_dir = repo_root / 'ai_models' / 'fine-tuned' / agent_name
    output_dir.mkdir(parents=True, exist_ok=True)
    train_args = SFTTrainingArguments(
        output_dir=str(output_dir / 'checkpoint'),
        per_device_train_batch_size=4,
        gradient_accumulation_steps=8,
        max_steps=1000,
        learning_rate=2e-4,
        logging_steps=20,
        save_strategy='steps',
        save_steps=200,
        bf16=True,
    )

    # Initialize SFT trainer
    trainer = SFTTrainer(
        model=model,
        train_dataset=train_data,
        peft_config=peft_config,
        dataset_text_field='text',
        args=train_args,
        tokenizer=tokenizer,
    )
    trainer.train()

    # Merge LoRA adapters and unload base layers
    trained_model = model.merge_and_unload()

    # Convert to GGUF with Q4_K_M quantization for llama-cpp-python
    gguf_path = output_dir / f"{agent_name}_q4.gguf"
    subprocess.run([
        'python3', '-m', 'llama_cpp.convert',
        '--model', str(base_model / 'pytorch_model.bin'),
        '--outfile', str(gguf_path),
        '--quantize', 'q4_K_M',
    ], check=True)

    print(f"GGUF model saved to: {gguf_path}")


if __name__ == '__main__':
    main()
