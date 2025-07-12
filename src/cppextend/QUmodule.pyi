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
def init_tray(tooltip:str, show_callback:function, about_callback:function, exit_callback:function) -> int:
    """
    tooltip: the tooltip to be displayed on the tray icon
    show_callback: the function to be called when the tray icon is clicked
    about_callback: the function to be called when the "About" menu item is clicked
    exit_callback: the function to be called when the "Exit" menu item is clicked
    return: 0 if successful, -1 if failed.
    """
    ...
def remove_tray() -> None:
    # remove the tray icon.
    ...
