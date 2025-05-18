from rembg import remove, new_session
from PIL import Image
import uuid
import os
import sys

from config import XTConfig


def generate_unique_hash():
    """生成一个唯一的哈希值"""
    return uuid.uuid4().hex[:8]  # 使用8位哈希值，可以根据需要调整长度


def process_image(input_path, output_path=None, bg_color=None, model=None):
    """
    使用rembg库处理图片，移除背景

    Args:
        input_path: 输入图片路径
        output_path: 输出图片路径或目录，如果为None则自动生成

    Returns:
        bool: 处理是否成功
        :param model:
        :param input_path:
        :param output_path:
        :param bg_color:
    """
    try:
        # 打开输入图片
        input_image = Image.open(input_path)

        if model is None:
            model = "u2net"
        session = new_session(model_name=model)

        if bg_color:
            try:
                # 移除可能的#前缀
                if bg_color.startswith('#'):
                    bg_color = bg_color[1:]

                # 解析颜色
                r = int(bg_color[0:2], 16)
                g = int(bg_color[2:4], 16)
                b = int(bg_color[4:6], 16)

                bgcolor = (r, g, b, 255)
                print(f"使用背景颜色: RGB({r}, {g}, {b})")
            except Exception as e:
                print(f"背景颜色格式错误: {str(e)}，将使用透明背景")
                bgcolor = None

        # 执行抠图
        output_image = remove(input_image, session=session, bgcolor=bgcolor)
        # 获取输入文件的文件名和扩展名
        input_filename, input_ext = os.path.splitext(os.path.basename(input_path))
        # 生成输出文件名
        output_filename = os.path.join(output_path, f"{input_filename}_{generate_unique_hash()}{input_ext}")
        # 确保输出目录存在
        output_dir = os.path.dirname(output_filename)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        print(f"文件保存至: {output_filename}")
        # 处理JPEG保存（不支持透明通道）
        if input_ext.lower() in ['.jpg', '.jpeg'] and output_image.mode == 'RGBA':
            # 创建RGB图像并粘贴RGBA图像
            rgb_image = Image.new('RGB', output_image.size, (255, 255, 255))
            rgb_image.paste(output_image, mask=output_image.split()[3])
            rgb_image.save(output_filename, 'JPEG', quality=95)
        else:
            output_image.save(output_filename)

        return True
    except Exception as e:
        print(f"处理图片时发生错误: {e}")
        return False


def remove_bg_process(config: XTConfig):
    """
    移除背景的主函数

    Args:
        config: 配置信息

    Returns:
        bool: 处理是否成功
        :param config:
    """
    output_path = config.output_path.joinpath("koutu")
    if not output_path.exists():
        output_path.mkdir(exist_ok=True, parents=True)
    success = process_image(config.input_path[0], output_path, config.removeBgConfig.bg_color,
                            config.removeBgConfig.model)
    sys.exit(0 if success else 1)
