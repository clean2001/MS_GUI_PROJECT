import sys, os


def return_root_dir():
    cur_path = os.path.dirname(os.path.realpath(__file__))
    cur_path = cur_path.replace('\\', '/')
    return cur_path
