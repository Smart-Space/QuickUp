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