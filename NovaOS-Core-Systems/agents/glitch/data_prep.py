import pandas as pd
from pathlib import Path


def collect_files(paths, exts):
    records = []
    for base_path in paths:
        for ext in exts:
            for fp in Path(base_path).rglob(f"*{ext}"):
                try:
                    text = fp.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                records.append({"filepath": str(fp), "content": text})
    return pd.DataFrame(records)


def main():
    # Determine repository root (assumes this file is under agents/glitch)
    repo_root = Path(__file__).resolve().parents[3]
    agent_name = "glitch"

    # Define source directories for code and config files
    shared_dirs = [
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

    # Prepare output directory
    out_dir = repo_root / 'data' / 'training' / agent_name
    out_dir.mkdir(parents=True, exist_ok=True)

    # Collect and write code files
    df_code = collect_files(shared_dirs, code_exts)
    df_code.to_parquet(out_dir / 'code.parquet', index=False)

    # Collect and write config files
    df_config = collect_files(shared_dirs, config_exts)
    df_config.to_parquet(out_dir / 'configs.parquet', index=False)


if __name__ == '__main__':
    main()
