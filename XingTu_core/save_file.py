from config import XTConfig
import os
import shutil


def save_file_progress(config: XTConfig):
    output_path = config.output_path
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
    for file_path in config.input_path:
        if file_path.is_file():
            file_name = os.path.basename(file_path)
            target_path = os.path.join(config.output_path, file_name)

            # 处理文件名冲突
            counter = 1
            while os.path.exists(target_path):
                name, ext = os.path.splitext(file_name)
                target_path = os.path.join(config.output_path, f"{name}_{counter}{ext}")
                counter += 1

            shutil.move(file_path, target_path)
            print(f"Moved: {file_path} -> {target_path}")
        else:
            print(f"Warning: {file_path} is not a valid file, skipped.")