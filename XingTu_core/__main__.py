import argparse
from config import XTConfig
from progress import progress
import os


parser = argparse.ArgumentParser(description="多功能图像处理工具")
parser.add_argument("-b", "--BASE64", help="base64 string for config json", type=str)
parser.add_argument("-j", "--JSON", help="JSON string for config", type=str)
parser.add_argument("-y", "--YAML", help="yaml config file path", type=str)

args = parser.parse_args()


def main():
    config: XTConfig
    if args.BASE64 is not None:
        config = XTConfig.from_base64(str(args.BASE64))
    elif args.JSON is not None:
        config = XTConfig.from_json_str(str(args.JSON))
    elif args.YAML is not None:
        config = XTConfig.from_yaml(str(args.YAML))
    return progress(config)


if __name__ == "__main__":
    main()
    
