from PIL import Image
import os
import uuid
from config import XTConfig


def generate_unique_hash():
    """生成一个唯一的哈希值"""
    return uuid.uuid4().hex[:8]  # 使用8位哈希值，可以根据需要调整长度


def compress_image(input_path, output_path, output_format='JPEG', quality=85):
    """
    压缩图片质量
    :param input_path: 输入图片路径
    :param output_path: 输出图片路径
    :param output_format: 输出图片格式（如 'JPEG', 'PNG', 'WEBP'）
    :param quality: 压缩质量(1-100)，数值越小压缩率越高
    :return: 是否压缩成功
    """
    try:
        with Image.open(input_path) as img:
            # 处理透明通道和调色板图像
            if img.mode in ('RGBA', 'P'):
                if output_format.upper() == 'JPEG':
                    img = img.convert('RGB')  # JPEG不支持透明通道
                elif output_format.upper() == 'PNG':
                    img = img.convert('RGBA')  # 保持透明通道
                elif output_format.upper() == 'WEBP':
                    img = img.convert('RGBA')  # WebP支持透明通道

            # 保存图片
            # 使用uuid生成唯一文件名
            input_filename, input_ext = os.path.splitext(os.path.basename(input_path))
            output_filename = f"{input_filename}_{generate_unique_hash()}.{output_format.lower()}"
            output_path = os.path.join(output_path, output_filename)
            print(f"文件保存至: {output_path}")
            img.save(output_path, format=output_format, quality=quality, optimize=True)

            # 获取压缩前后文件大小
            original_size = os.path.getsize(input_path)
            compressed_size = os.path.getsize(output_path)
            print(f"压缩完成: 原始大小 {original_size / 1024:.2f} KB, 压缩后 {compressed_size / 1024:.2f} KB")
            print(f"压缩比例: {(1 - compressed_size / original_size) * 100:.2f}%")

            return True
    except Exception as e:
        print(f"压缩失败: {e}")
        return False


def compress_process(config: XTConfig):
    output_path = config.output_path.joinpath("compress")
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
    compress_image(config.input_path[0], output_path, config.compressConfig.target_format,
                   config.compressConfig.quality)
