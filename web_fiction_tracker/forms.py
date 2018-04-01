def verify_keys(dict_check, *args):
    bool_list = [(arg in dict_check) for arg in args]
    return bool_list