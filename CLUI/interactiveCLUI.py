import sys,tty,termios
from constants import cursorMoves,keys,colors


##########      Useful Functions       ################

# hides the cursor
def hide_cursor():
    print(cursorMoves.HIDE,end='')

# shows the cursor
def show_cursor():
    print(cursorMoves.SHOW,end='')

# clears the previous line, leaves cursor at beginning of previous line
def clear_prevline():
    sys.stdout.write(f"{cursorMoves.PREV_LINE}{cursorMoves.CLEAR}")

# Blocking read of one input character, handling appropriate interrupts
def get_ch():
    k = sys.stdin.read(1)[0]
    if k in {keys.END_OF_TEXT, keys.END_OF_FILE, keys.CANCEL}: raise KeyboardInterrupt
    return k

# clear 'num_lines' from console. Cursor is left where it was before function call
def clear_lines(num_lines):

    for _ in range(num_lines):
        print(cursorMoves.CLEAR)

    for _ in range(num_lines):
        sys.stdout.write(cursorMoves.PREV_LINE) 

# prints a prompt with formatting
# allows consistent colors, indenting, effects etc. between different types prompt
def print_prompt(prompt,end='\n'):
    print(f"{colors.BOLD}{colors.GREEN} ? {colors.END}{colors.BOLD}{prompt}{colors.END}",end=end)

# prints a prompt and chosen option with formatting
# allows consistent colors, indenting, effects etc. between different types prompt
def print_prompt_and_option(prompt,option:str):
    print(f"{colors.BOLD}{prompt}{colors.END} - {colors.CYAN}{option}{colors.END}")

# prints a prompt and chosen options with formatting
# allows consistent colors, indenting, effects etc. between different types prompt
def print_prompt_and_options(prompt,options:list[str],selected_boxes):
    print(f"{colors.BOLD}{prompt}{colors.END} - {colors.CYAN}", end='')
    for i, option in enumerate(options):
        if i in selected_boxes:
            print(f"{option}, ", end='')
    print(colors.END)


##########      Function 1       ################

# print the options for users to see, with selected option highlighted
def print_options(options, selected):
    for i, option in enumerate(options):
        if i == selected:
            output = f"{colors.CYAN}{colors.BOLD} > {option}{colors.END}"
        else:
            output = f"   {option}"
        print(f'\r{cursorMoves.CLEAR}{output}')
    print(cursorMoves.PREV_LINE * (len(options) + 1))

# handles user input to change the selected option
def handle_options(options):
    selected_option = 0
    length = len(options)
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:

        # Enter raw mode (key events sent directly as characters)
        tty.setraw(sys.stdin.fileno())

        # Loop, waiting for keyboard input
        while 1:

            # Parse known command escape sequences
            read = get_ch()
            while any(k.startswith(read) for k in keys.commands): 
                if read == keys.ARROW_UP or read == keys.PAGE_UP:
                    selected_option = (selected_option-1)%length
                    break
                elif read == keys.ARROW_DOWN or read == keys.PAGE_DOWN:
                    selected_option = (selected_option+1)%length
                    break
                elif read == keys.ENTER:
                    return selected_option
                read += get_ch()
            for c in read:
                if c == ' ':
                    return selected_option
                
            print_options(options,selected_option)
                
    # handle interrupts caused by getch
    except:
        show_cursor()
        clear_lines(len(options))
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings) 
        raise KeyboardInterrupt
        # sys.exit(1)

# gives users ui to choose an option using arrow keys 
def select_option(prompt:str, options:list[str]):
    hide_cursor()
    
    # preserve current terminal settings
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    selected_option = 0

    print_prompt(prompt)
    print_options(options, selected_option)

    selected_option = handle_options(options)

    clear_lines(len(options))
    show_cursor()

    # restore previous terminal settings
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    # delete previous prompt (that was in form '? prompt')
    clear_prevline()
    
    # print prompt with chosen option (in form 'prompt - option')
    print_prompt_and_option(prompt,options[selected_option])

    return options[selected_option],select_option

##########      Function 2       ################

# print the options for users to see, with selected option highlighted
def print_multiple_options(options, hovered, selected_list):
    for i, option in enumerate(options):
        if i in [num % len(options) for num in selected_list]:
            if i == hovered % len(options):
                output = f"{colors.BLUE}{colors.BOLD} {chr(0x25CF)} {option}{colors.END}"
            else:
                output = f"{colors.GREEN} {chr(0x25CF)} {option}{colors.END}"
        else:
            if i == hovered % len(options):
                output = f"{colors.CYAN}{colors.BOLD} {chr(0x25CB)} {option}{colors.END}"
            else:
                output = f"   {option}"
        print('')
        clear_prevline()
        print(f'{output}')
    print(cursorMoves.PREV_LINE * (len(options) + 1))

# handles user input to change the selected option
def handle_multiple_options(options,selected_boxes:list):
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    length = len(options)
    try:
        hovered = 0
        # Enter raw mode (key events sent directly as characters)
        tty.setraw(fd)

        # Loop, waiting for keyboard input
        while 1:
            # Parse known command escape sequences
            read = get_ch()
            
            while any(k.startswith(read) for k in keys.commands): 
                if read == keys.ARROW_UP or read == keys.PAGE_UP:
                    hovered = (hovered-1)%length
                    break
                elif read == keys.ARROW_DOWN  or read == keys.PAGE_DOWN:
                    hovered = (hovered+1)%length
                    break
                elif read == keys.ENTER:
                    return
                read += get_ch()

            # Interpret all other inputs as text input
            for c in read:
                if c == ' ':
                    if hovered in selected_boxes:
                        selected_boxes.remove(hovered)
                    else:
                        selected_boxes.append(hovered)


            print_multiple_options(options,hovered,selected_boxes)
            
    except KeyboardInterrupt:
        # in case of interrupt, revert back to original settings
        show_cursor()
        clear_lines(len(options))
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings) 
        # sys.exit(1)
        raise KeyboardInterrupt

# gives users ui to choose multiple options using arrow keys
def select_multiple_options(prompt:str, options:list[str]):
    hide_cursor()
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    print(f"{colors.BOLD}{colors.GREEN} ? {colors.END}{colors.BOLD}{prompt}{colors.END}")
    selected_boxes = []
    print_multiple_options(options, 0, selected_boxes)

    handle_multiple_options(options, selected_boxes)

    clear_lines(len(options))
    show_cursor()

    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    clear_prevline()

    print_prompt_and_options(prompt,options,selected_boxes)

    return [option for i, option in enumerate(options) if i in selected_boxes]

##########      Other Functions       ################

# Gives a prompt and opportunity for user to input text
# 'default' parameter: If user does not input anything, value of 'default' is returned
def input_text(prompt:str,default=None):
    if not default:
        print_prompt(f'{prompt} > ',end='')
    else:
        print_prompt(f'{prompt} ({default}) > ',end='')
    try:
        res = input()
    except KeyboardInterrupt:
        print(cursorMoves.PREV_LINE + cursorMoves.DOWN + cursorMoves.CLEAR,end='')
        print_prompt_and_option(prompt,'')
        raise KeyboardInterrupt
        # sys.exit(1)

    if res == '' and default:
        res = default
    clear_prevline()
    print_prompt_and_option(prompt,res)
    return res

# Gives a prompt and opportunity for user to input text in order to choose from a list of options
# 'default' parameter: If user does not input anything, value of 'default' is returned
def input_text_with_options(prompt:str,options:str,default=None):
    options = options.lower()
    default = default.lower()
    option_text = ''
    for c in options:
        if c==default:
            option_text += f'{c.upper()}/'
        else:
            option_text += f'{c}/'
    option_text = option_text[:-1]
    
    print_prompt(f'{prompt} ({option_text}) > ',end='')

    try:
        res = input().lower()
    except:
        print(cursorMoves.PREV_LINE + cursorMoves.DOWN + cursorMoves.CLEAR,end='')
        print_prompt_and_option(prompt,'')
        raise KeyboardInterrupt
        # sys.exit(1)

    if res == '' and default:
        res = default.upper()
    clear_prevline()
    print_prompt_and_option(prompt,res)
    return res

# Gives a prompt and opportunity for user to input text in order to choose 'y' (yes) or 'n'(no)
# 'default' parameter: If user does not input anything, value of 'default' is returned
def input_yesorno(prompt:str,default=None):
    if default:
        res = input_text_with_options(prompt,'yn',default.lower())
    else:
        res = input_text_with_options(prompt,'yn')
    return res

# TODO: add filter option
