from config import XTConfig
from format import format_progress
from remove_bg import remove_bg_process
from compress import compress_process
from final2x import final2x_progress


def progress(config: XTConfig):
    if config.command == 'format':
        format_progress(config)
    elif config.command == 'remove_bg':
        remove_bg_process(config)
    elif config.command == 'compress':
        compress_process(config)
    elif config.command == 'final2x':
        final2x_progress(config)
    else:
        print('Invalid command')
