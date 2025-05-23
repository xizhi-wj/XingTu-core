from config import XTConfig
from format import format_progress
from remove_bg import remove_bg_process
from compress import compress_process
from final2x import final2x_progress


def progress(config: XTConfig):
    if config.command == 'format':
        return format_progress(config)
    elif config.command == 'remove_bg':
        return remove_bg_process(config)
    elif config.command == 'compress':
        return compress_process(config)
    elif config.command == 'final2x':
        return final2x_progress(config)
    else:
        print('Invalid command')
        return 0
