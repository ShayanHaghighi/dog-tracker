# ANSI escape codes to format text
class colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WHITE = '\033[37m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# ANSI escape codes to move cursor
class cursorMoves:
    DOWN = '\033[B'
    PREV_LINE = '\033[F'
    CLEAR     = '\033[2K'
    HIDE      = '\033[?25l'
    SHOW      = '\033[?25h'

class keys():
    # Commands and escape codes
    END_OF_TEXT = chr(3)  # CTRL+C
    END_OF_FILE = chr(4)  # CTRL+D
    CANCEL      = chr(24) # CTRL+X
    ESCAPE      = chr(27) # Escape
    CONTROL     = ESCAPE +'['

    # Escape sequences for terminal keyboard navigation
    ARROW_UP    = CONTROL+'A'
    ARROW_DOWN  = CONTROL+'B'
    PAGE_UP     = CONTROL+'5~'
    PAGE_DOWN   = CONTROL+'6~'
    ENTER       = '\r'

    # Escape sequences to match
    commands = [
        ARROW_UP,
        ARROW_DOWN,
        ENTER,
        PAGE_UP,
        PAGE_DOWN
    ]
