def to_string(arg_list):
    ret_str = ""
    for pair in arg_list:
        ret_str += pair[0] + ": " + str(int(pair[1]/60)) + " minutes\n"
    return ret_str
