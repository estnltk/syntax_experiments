import os

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
parent_folder = os.path.dirname(script_dir)

PATH_ROOT = parent_folder
PATH_COMMON_CODE = script_dir
