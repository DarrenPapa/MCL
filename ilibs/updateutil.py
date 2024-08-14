# Do not modify carelessly
# This is used by mcl.py to handle
# Updates

# HANDLE WITH INTENSE CARE

# Contributors:
#     Darren Chase Papa

import tomllib as toml
from itertools import zip_longest
from os import path

def parse_file(fpath):
    if not path.isfile(fpath):
        return {}
    else:
        with open(fpath, "rb") as f:
            return toml.load(f)

def standard_ver(ver_str):
    major, minor = ver_str.split(".",1)
    minor, build = minor.split("-",1)
    return int(major), int(minor), ord(build.upper())-64

def common_ver(ver_str):
    major, minor, build = ver_str.split(".",2)
    return int(major), int(minor), int(build)

def compare_ver(tuple1, tuple2):
    for new, old in zip_longest(tuple1, tuple2, fillvalue=0):
        if new < old:
            return False
        elif new > old:
            return True
    return True

def gen_name(libs, name):
    name = f"{libs}-{path.basename(name).split('.')[0]}.toml"
    return name

def check_ver(new, old):
    # standard is number.number-character
    if new["format"] == "standard" and old["format"] == "standard":
        new_ver = standard_ver(new["version"])
        old_ver = standard_ver(old["version"])
        if compare_ver(new_ver, old_ver):
            return True
        else:
            return False
    # float is well a float
    elif new["format"] == "float" and old["format"] == "float":
        new_ver = float(new["version"])
        old_ver = float(old["version"])
        if new_ver > old_ver:
            return True
        else:
            return False
    # common is number.number.number
    elif new["format"] == "common" and old["format"] == "common":
        new_ver = common_ver(new["version"])
        old_ver = common_ver(old["version"])
        if compare_ver(new_ver, old_ver):
            return True
        else:
            return False
    else:
        raise Exception("Version format is invalid!")