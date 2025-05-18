from config import XTConfig
from format import format_progress
from remove_bg import remove_bg_process
from compress import compress_process


def progress(config: XTConfig):
    if config.command == 'format':
        format_progress(config)
    elif config.command == 'remove_bg':
        remove_bg_process(config)
    elif config.command == 'compress':
        compress_process(config)
    elif config.command == 'save_file':
        pass
    else:
        print('Invalid command')
