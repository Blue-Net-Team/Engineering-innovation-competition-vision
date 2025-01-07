from typing import Any, get_origin, get_args

def check_args(*args: tuple[Any, type]):
    """
    检查重载函数的参数类型
    ----
    Args:
        *args: 变量，类型组
    """
    for arg, arg_type in args:
        origin_type = get_origin(arg_type)
        if origin_type is list:
            item_type = get_args(arg_type)[0]
            if not (isinstance(arg, list) and all(isinstance(item, item_type) for item in arg)):
                return False, "Expected List[{item_type}], but got {arg}"
        else:
            if not isinstance(arg, arg_type):
                return False, "Expected {arg_type}, but got {arg}"
    return True, ""

