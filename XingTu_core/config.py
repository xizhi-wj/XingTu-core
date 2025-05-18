from pydantic import BaseModel, DirectoryPath, FilePath, Field
from pathlib import Path
import yaml
import json
import base64
from typing import List, Union, Optional, Literal

# 定义可能的枚举类型（根据 TypeScript 的 ImageFormat 和 XingTuCommand 调整）
ImageFormat = Literal["jpg", "png", "webp"]  # 假设 ImageFormat 是这些值
XingTuCommand = Literal["format", "compress", "remove_bg", "save_file"]  # 假设 Command 是这些值


class FormatConfig(BaseModel):
    target_format: str


class CompressConfig(BaseModel):
    target_format: ImageFormat
    quality: int = Field(ge=1, le=100)  # 限制 quality 在 1-100 之间


class RemoveBgConfig(BaseModel):
    bg_color: str
    model: str


class XTConfig(BaseModel):
    command: XingTuCommand
    output_path: DirectoryPath
    input_path: List[FilePath]
    task_id: Optional[str] = None
    formatConfig: Optional[FormatConfig] = None
    compressConfig: Optional[CompressConfig] = None
    removeBgConfig: Optional[RemoveBgConfig] = None

    @classmethod
    def from_yaml(cls, yaml_path: Union[Path, str]) -> "XTConfig":
        """从 YAML 文件加载配置"""
        with open(yaml_path, "r", encoding="utf-8") as f:
            try:
                config = yaml.safe_load(f)
            except Exception as e:
                raise ValueError(f"Error loading YAML config: {e}")
        return cls(**config)

    @classmethod
    def from_json_str(cls, json_str: str) -> "XTConfig":
        """从 JSON 字符串加载配置"""
        try:
            config = json.loads(json_str)
        except Exception as e:
            raise ValueError(f"Error parsing JSON config: {e}")
        return cls(**config)

    @classmethod
    def from_base64(cls, base64_str: str) -> "XTConfig":
        """从 Base64 字符串加载配置"""
        try:
            config_bytes = base64.b64decode(base64_str.encode("utf-8"))
            config_json_str = config_bytes.decode("utf-8")
            return cls.from_json_str(config_json_str)
        except Exception as e:
            raise ValueError(f"Error decoding Base64 config: {e}")

    def to_dict(self) -> dict:
        """将配置转换为字典（可用于 JSON 序列化）"""
        return self.dict(exclude_none=True)  # 排除 None 字段
