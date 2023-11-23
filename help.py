import configparser

helpfile = configparser.ConfigParser()
helpfile.read("help.ini")

def show_commands():
    cor = ""
    for c in helpfile['commands']:
        cor += "!" + c + " : "
        cor += helpfile['commands'][c] + "\n"
    return cor


def show_debug():
    cor = ""
    for c in helpfile['debug']:
        cor += "!" + c + " : "
        cor += helpfile['debug'][c] + "\n"
    return cor


def get(command):
    if helpfile['commands'][command] is not None:
        return helpfile['commands'][command]
    elif helpfile['debug'][command] is not None:
        return helpfile['debug'][command]
    else:
        return None
