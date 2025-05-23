from config import XTConfig
from loguru import logger
from pathlib import Path
import torch
import cv2
import numpy as np
import math
from typing import Any, List, Optional, Union
from ccrestoration import AutoModel, SRBaseModel
from ccrestoration import AutoConfig, BaseConfig, ConfigType
from ccrestoration.util.device import default_device

def get_device(device: str) -> Union[torch.device, str]:
    """
    Get device from string

    :param device: device string
    """
    if device.startswith("auto"):
        return default_device()
    elif device.startswith("cpu"):
        return torch.device("cpu")
    elif device.startswith("cuda"):
        return torch.device("cuda")
    elif device.startswith("mps"):
        return torch.device("mps")
    elif device.startswith("directml"):
        import torch_directml

        return torch_directml.device()
    elif device.startswith("xpu"):
        return torch.device("xpu")
    else:
        print(f"Unknown device: {device}, use auto instead.")
        return default_device()

def singleton(cls):
    """
    singleton decorator
    """
    instances = {}

    def getinstance(*args, **kw):
        if cls not in instances:
            if isinstance(cls, type):
                instances[cls] = cls(*args, **kw)
            else:
                instances[cls] = cls

        return instances[cls]

    if isinstance(cls, type):
        return getinstance
    else:
        return getinstance(cls)


@singleton
class PrintProgressLog:
    def __init__(self) -> None:
        """
        Total: Total Process Time
        """

        self.Total = 0
        self.progressCurrent = 0
        self.sr_n = 1

    @logger.catch(reraise=True)  # type: ignore
    def set(self, total_file: int, sr_n: int) -> None:
        if total_file <= 0:
            raise AssertionError("Total must be greater than 0")
        if sr_n < 1:
            raise AssertionError("sr_n must be greater than 1")
        self.Total = total_file * sr_n
        self.sr_n = sr_n

    @logger.catch  # type: ignore
    def printProgress(self) -> None:
        self.progressCurrent += 1
        percentage: float = round(self.progressCurrent / self.Total * 100, 1)
        logger.info("Processing------[ " + str(percentage) + "% ]")

    @logger.catch  # type: ignore
    def skipProgress(self) -> None:
        for _ in range(self.sr_n):
            self.printProgress()

class CCRestoration:
    """
    Super-resolution class for processing images, using ccrestoration.

    :param config: XTConfig
    """

    def __init__(self, config: XTConfig) -> None:
        self.config: XTConfig = config

        PrintProgressLog().set(len(self.config.input_path), 1)

        self._SR_class: SRBaseModel = AutoModel.from_pretrained(
            pretrained_model_name=self.config.pretrained_model_name,
            fp16=False,
            device=get_device(self.config.device),
            gh_proxy=self.config.gh_proxy,
        )

        logger.info("SR Class init, device: " + str(self._SR_class.device))

    @logger.catch  # type: ignore
    def process(self, img: np.ndarray) -> np.ndarray:
        """
        set target size, and process image
        :param img: img to process
        :return:
        """

        _target_size = (
            math.ceil(img.shape[1] * self.config.target_scale),
            math.ceil(img.shape[0] * self.config.target_scale),
        )

        img = self._SR_class.inference_image(img)
        PrintProgressLog().printProgress()

        if abs(float(self.config.target_scale) - float(self.config.cc_model_scale)) < 1e-3:  # type: ignore
            return img

        img = cv2.resize(img, _target_size, interpolation=cv2.INTER_LINEAR)

        return img

def sr_queue(config: XTConfig) -> None:
    """
    Super-resolution queue. Process all RGBA images according to the config.

    :param config: XTConfig
    :return:
    """
    input_path: List[Path] = config.input_path
    output_path: Path = config.output_path / "outputs"
    output_path.mkdir(parents=True, exist_ok=True)  # create output folder
    sr = CCRestoration(config)

    logger.info("Processing------[ 0.0% ]")

    for img_path in input_path:
        save_path = str(output_path / (Path(str(config.target_scale) + "x-" + Path(img_path).name).stem + ".png"))

        i: int = 0
        while Path(save_path).is_file():
            logger.warning("Image already exists: " + save_path)
            i += 1
            save_path = str(
                output_path
                / (Path(str(config.target_scale) + "x-" + Path(img_path).name).stem + "(" + str(i) + ").png")
            )
            logger.warning("Try to save to: " + save_path)

        if not Path(img_path).is_file():
            logger.error("File not found: " + str(img_path) + ", skip. Save path: " + save_path)
            logger.warning("______Skip_Image______: " + str(img_path))
            PrintProgressLog().skipProgress()

        else:
            alpha_channel = None

            try:
                # The file may not be read correctly.
                # In unix-like system, the Filename Extension is not important.
                img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)

                if len(img.shape) == 2:
                    logger.warning("Grayscale image detected, Convert to RGB image.")
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

                elif img.shape[2] == 4:
                    logger.warning("4 channels image detected.")
                    PrintProgressLog().Total += PrintProgressLog().sr_n
                    # Extract alpha channel
                    alpha_channel = img[:, :, 3]
                    # Remove alpha channel from the image
                    img = img[:, :, :3]

                if img is None:
                    raise Exception("Failed to decode image.")
            except Exception as e:
                logger.error(str(e))
                logger.warning("CV2 load image failed: " + str(img_path) + ", skip. ")
                logger.warning("______Skip_Image______: " + str(img_path))
                PrintProgressLog().skipProgress()
                continue

            logger.info("Processing: " + str(img_path) + ", save to: " + save_path)
            img = sr.process(img)

            if alpha_channel is not None:
                # Stack alpha channel into a 3-channel tensor (AAA)
                alpha_tensor = np.dstack((alpha_channel, alpha_channel, alpha_channel))
                # Apply super-resolution to the alpha tensor
                alpha_tensor = sr.process(alpha_tensor)
                # Merge processed RGB channels with processed alpha tensor
                img = np.dstack((img, alpha_tensor[:, :, 0]))

            cv2.imencode(".png", img)[1].tofile(save_path)

            logger.success("______Process_Completed______: " + str(img_path))

def final2x_image(config: XTConfig):
    logger.info("config loaded")
    logger.debug("output path: " + str(config.output_path))
    sr_queue(config)
    logger.success("______SR_COMPLETED______")

def final2x_progress(config: XTConfig):
    if config.final2xConfig is None:
        return False
    c: BaseConfig = AutoConfig.from_pretrained(pretrained_model_name=config.final2xConfig.pretrained_model_name)
    config.final2xConfig.cc_model_scale = c.scale
    if config.final2xConfig.target_scale is None or config.final2xConfig.target_scale <= 0:
        config.final2xConfig.target_scale = c.scale
    final2x_image(config.final2xConfig)