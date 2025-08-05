import pandas as pd
from pathlib import Path
import json
import yaml
import toml
from typing import List, Dict, Union


def collect_files(paths: List[Path], exts: List[str]) -> pd.DataFrame:
    """
    Recursively collects files with specified extensions from given paths,
    returning their absolute paths and decoded content.

    Args:
        paths (List[Path]): Base directories to search.
        exts (List[str]): File extensions to include (e.g., ['.py', '.json']).

    Returns:
        pd.DataFrame: DataFrame with columns: ['filepath', 'content']
    """
    records = []
    for base_path in paths:
        for ext in exts:
            for fp in base_path.rglob(f"*{ext}"):
                try:
                    content = fp.read_text(encoding="utf-8", errors="ignore")
                    records.append({"filepath": str(fp.resolve()), "content": content})
                except Exception:
                    continue
    return pd.DataFrame(records)


def parse_config_files(df: pd.DataFrame) -> List[Dict[str, Union[str, dict]]]:
    """
    Parses config files into structured Python objects where possible.

    Args:
        df (pd.DataFrame): DataFrame containing filepaths and raw content.

    Returns:
        List[Dict]: List of dicts with filepath, raw content, and parsed config (if possible).
    """
    parsed = []
    for _, row in df.iterrows():
        parsed_entry = {
            "filepath": row["filepath"],
            "content": row["content"],
            "parsed": None
        }
        try:
            if row["filepath"].endswith(".json"):
                parsed_entry["parsed"] = json.loads(row["content"])
            elif row["filepath"].endswith((".yaml", ".yml")):
                parsed_entry["parsed"] = yaml.safe_load(row["content"])
            elif row["filepath"].endswith(".toml"):
                parsed_entry["parsed"] = toml.loads(row["content"])
        except Exception:
            pass
        parsed.append(parsed_entry)
    return parsed


def main():
    # Determine repo root (expects this file inside agents/audita)
    repo_root = Path(__file__).resolve().parents[3]
    agent_name = "audita"

    # Define source directories and extensions
    source_dirs = [
        repo_root / 'agents' / agent_name,
        repo_root / 'core',
        repo_root / 'plugins',
        repo_root / 'configs',
        repo_root / 'scripts',
        repo_root / 'blackrose',
        repo_root / 'gypsycove'
    ]
    code_exts = ['.py', '.sh']
    config_exts = ['.json', '.yaml', '.yml', '.toml']

    # Output directory
    output_dir = repo_root / 'data' / 'training' / agent_name
    output_dir.mkdir(parents=True, exist_ok=True)

    # Code files
    df_code = collect_files(source_dirs, code_exts)
    df_code.to_parquet(output_dir / 'code.parquet', index=False)

    # Config files
    df_config = collect_files(source_dirs, config_exts)
    df_config.to_parquet(output_dir / 'configs_raw.parquet', index=False)

    # Parsed config structures
    parsed_configs = parse_config_files(df_config)
    df_parsed = pd.DataFrame(parsed_configs)
    df_parsed.to_parquet(output_dir / 'configs_parsed.parquet', index=False)


if __name__ == '__main__':
    main()
