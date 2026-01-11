def get_parent(hwnd:int) -> int:
    """
    hwnd: the handle of the child window
    return: the handle of the parent window
    """
    ...
def get_windowtext(hwnd:int) -> str|False:
    """
    hwnd: the handle of the window
    return: the text of the window, or False if the window is not valid.
    """
    ...
def priority_window(name:str|int) -> bool:
    """
    name: the title of a window, or the handle of the window
    return: True if successful, False otherwise.
    """
def is_msix() -> bool:
    # return True if running as an MSIX package, False otherwise.
    ...
def window_no_icon(hwnd:int) -> None:
    # remove the icon from the window.
    ...
def set_window_dark(hwnd:int) -> None:
    # set dark mode
    ...
def shell_execute_wrapper(cmd:str, args:str, cwd:str, maximize:int, minimize:int, operation:str) -> str:
    """
    cmd: the command to be executed
    args: the arguments to be passed to the command
    cwd: the working directory for the command
    maximize: 1 to maximize the window, 0 to not maximize
    minimize: 1 to minimize the window, 0 to not minimize
    operation: the operation to be performed
    return: the return error information if the operation fails, or an empty string otherwise.
    """
    ...
def shell_execute_ex_wrapper(cmd:str, args:str, cwd:str, maximize:int, minimize:int, admin:int, name:str) -> str:
    """
    cmd: the command to be executed
    args: the arguments to be passed to the command
    cwd: the working directory for the command
    maximize: 1 to maximize the window, 0 to not maximize
    minimize: 1 to minimize the window, 0 to not minimize
    admin: 1 to run the command as an administrator, 0 to not run as an administrator
    name: the name of the window to be created
    return: the return error information if the operation fails, or an empty string otherwise.
    """
    ...
def run_console_commands(cmd:str, cmds:list, cwd:str, wait:bool) -> None:
    """
    cmd: the command to be executed
    cmds: a list of commands to be executed in sequence
    cwd: the working directory for the command
    wait: True to wait for the command to finish, False to run in the background
    """
    ...
def quick_fuzz(list:list, name:str, acc:int, num:int) -> list:
    """
    list: list of strings to be fuzzed
    name: the string to be fuzzed
    acc: the accuracy of the fuzzing
    num: the number of fuzzed strings to be returned
    return: a list of fuzzed strings
    """
    ...
def register_start(value: str, path: str) -> int:
    # return 0 if successful, -1 if failed.
    ...
def unregister_start(value: str) -> int:
    # return 0 if successful, -1 if failed.
    ...
def have_start_value(value: str) -> bool:
    # return True if value is registered, False otherwise.
    ...
def create_link(app:str, cmd:str, lnkpath:str, icopath:str) -> bool:
    """
    app: the application to be launched
    cmd: the command line arguments to be passed to the application
    lnkpath: the path of the shortcut to be created
    icopath: the path of the icon to be used for the shortcut
    return: True if successful, False otherwise.
    """
    ...
def init_tray(window:int, tooltip:str, about_callback:function, exit_callback:function) -> int:
    """
    window: the handle of the main window
    tooltip: the tooltip to be displayed on the tray icon
    about_callback: the function to be called when the "About" menu item is clicked
    exit_callback: the function to be called when the "Exit" menu item is clicked
    return: 0 if successful, -1 if failed.
    """
    ...
def remove_tray() -> None:
    # remove the tray icon.
    ...
def enable_entry_drop(hwnd:int, callback:function) -> object:
    """
    hwnd: the handle of the control to enable drop target
    callback: the function to be called when a file is dropped on the control
    return: a handle to the drop target object.
    """
    ...
def disable_entry_drop(dt:object) -> None:
    # delete (but not disable) the drop target object.
    # use when control is destroyed.
    ...
def is_valid_windows_filename(name:str) -> bool:
    """
    name: the filename to be checked
    return: True if name is a valid Windows filename, False otherwise.
    """
    ...
def start_hotkey(fsmodifier:int, fskey:int, callback:function) -> None:
    """
    fsmodifier: the modifier key for the hotkey (e.g. MOD_ALT)
    fskey: the key code for the hotkey (e.g. ord('Q'))
    callback: the function to be called when the hotkey is pressed
    """
    ...
def stop_hotkey() -> None:
    # stop the hotkey.
    ...
def detect_app_theme() -> str:
    """
    return: "dark" or "light" depending on the current Windows theme.
    """
    ...