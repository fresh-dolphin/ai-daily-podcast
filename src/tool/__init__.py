import json
import os
from datetime import datetime
from pathlib import Path

def get_output_dir(project_root_dir: Path) -> Path:
    today = datetime.today().strftime('%Y-%m-%d')

    out_dir = Path(f"{project_root_dir}/out/{today}/")
    out_dir.mkdir(parents=True, exist_ok=True)

    return out_dir

def save_dict_to_file(dictionary, file_path):
    if os.path.exists(file_path):
        print(f"file {file_path} exists from previous execution, overriding...")
    with open(file_path, 'w+') as f:
        json.dump(dictionary, f, indent=2, ensure_ascii=False)

def save_text_to_file(text, file_path):
    if os.path.exists(file_path):
        print(f"file {file_path} exists from previous execution, overriding...")
    with open(file_path, 'w+') as f:
        f.write(text)