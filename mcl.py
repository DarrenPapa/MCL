#!/usr/bin/env python3

# MCL or My Complicated #Language
# A simple compiled and interrpeted programming
# language.
# Developed by:
#     Darren Chase Papa - Founder
# Version 0.1

# "Complex behavior arises from 
#                            even the simplest of things"
#
#                               - Darren Chase Papa, 2024

# File types:
#   Compiled            - *.cmcl  (compiled mcl file)
#   Normal              - *.mcl
#   Data                - *.pkl
#   Pickling uses the dill library to be able to pickle
#   functions.

from ilibs.check_libs import check_lib

if r:=check_lib():
    print(f"Missing dependency please install the required dependency or\nrun `ensure_dep` in ilibs.\nLibrary: {r}")
    exit(1)

from sys import exit # For pyinstaller
import cProfile
import dill
import time
import traceback
import cffi
import ilibs.easteregg
import __main__ as main_file
from importlib import reload
from os.path import isfile, isdir, basename, dirname, join
from os import makedirs
from sys import argv
from sys import version
from ilibs.compiler import compiler, pack, unpack
from ilibs.info import VERSION as VER, LIBDIR, BINDIR, GLOBAL, SYSTEM_NAME as I_SN, SYSTEM_BUILD_NAME as I_SBN, SYSTEM_ARCH as I_SA, SUPORTED as SUP, ISSUPORTED as I_SUP
from ilibs.mem_monitor import monitor_memory, monitor_memory_highres
if not isdir(LIBDIR):
    makedirs(LIBDIR)
if not isfile(GLOBAL):
    with open(GLOBAL, "wb") as f:
        f.write(dill.dumps({}))
globs = dill.loads(open(GLOBAL,"rb").read())
i_info = "NO_INTERPRETER_INFO" not in globs
# cparser.cpython-311.so is not available yet
# since this was developed in Pydroid3
# on a android 14 device
# Try to use compiled parsers
try:
    if I_SN == "posix": # Linux or MacOS
        from ilibs.cparser import parse
    elif I_SN == "nt":  # Windows
        from ilibs.cparser_win import parse
    else:
        print("Unknown system!")
        raise ImportError()
except ImportError:
   print("Warning: Could not use faster options!")
   from ilibs.parser import parse
   print("Info: Fall back to 'parser.py'...\nPerformance drops may be noticable!\n")
VER_STR = f"""+-------------{'-'*(len(VER)+2)}-+
| MCL Version [{VER}] |
+-----{'-'*(len(VER)+2)}-07-2024-+"""
VER_GOOF = f"""+------------------{'-'*(len(VER)+2)}-+
| Goof MCL Version [{VER}] |
| You found an easter egg! {' '*(len(VER)-5)}|
+----------{'-'*(len(VER)+2)}-07-2024-+

On System: {I_SN}
On Build: {I_SBN}
On Architecture: {I_SA}
Current Build In Supported: {I_SUP}
Systems Supported: {', '.join(map(str.capitalize,SUP))}

Contributor(s):
  - Darren Chase Papa"""
VER_SERIOUS = f"""+-------------{'-'*(len(VER)+2)}-+
| MCL Version [{VER}] |
+-----{'-'*(len(VER)+2)}-07-2024-+

On System: {I_SN}
On Build: {I_SBN}
On Architecture: {I_SA}
Current Build In Supported: {I_SUP}
Systems Supported: {', '.join(map(str.capitalize,SUP))}

Contributor(s):
  - Darren Chase Papa"""
def reload_script():
    reload(main_file)
def forms(o):
    return f'"{o}"' if " " in o else o
def main():
    match argv[1:]:
        case ["run", path, *args]:
            g = {f"argv{pos}":value for pos, value in enumerate([path, *args])}
            if not isfile(path):
                print(f"The path `{path}` is invalid!")
                exit(1)
            try:
                with open(path, "r") as file:
                    code = file.read()
            except:
                print(f"`{path}` cannot be opened!")
                if path.endswith(".cmcl"):
                    print(f"Did you mean:\n`mcl.py run \"{path}\"" + ((" "+" ".join(map(forms,args))+"`") if args else "`"))
                exit(1)
            try:
                res = parse(code, g, globs=globs)
            except KeyboardInterrupt:
                print("KeyboardInterrupt!")
                res = 0
            if res != 0 and not isinstance(res, tuple):
                print("Error!")
                exit(1)
        case ["analyze", path, *args]:
            g = {f"argv{pos}":value for pos, value in enumerate([path, *args])}
            if not isfile(path):
                print(f"The path `{path}` is invalid!")
                exit(1)
            try:
                with open(path, "r") as file:
                    code = file.read()
            except:
                print(f"`{path}` cannot be opened!")
                exit(1)
            try:
                res = parse(code, g, globs=globs)
            except KeyboardInterrupt:
                print("KeyboardInterrupt!")
                res = 0
            if res != 0 and not isinstance(res, tuple):
                print("Error!")
                if path.endswith(".cmcl"):
                    print(f"Did you mean:\n`mcl.py ac \"{path}\"" + ((" "+" ".join(map(forms,args))+"`") if args else "`"))
                exit(1)
            _, dv, ff = res
            if dv:
                print("Variables:")
                ml = max(map(len, dv))
                for i in dv:
                    print(f"  {'`'+i.rjust(ml)+'`'}", end="")
                    if i.startswith("-"):
                        print(" - May be used for configs!")
                    else:
                        print()
            if ff:
                print("Subroutines and Labels:")
                ml = max(map(len, ff))
                for i in ff:
                    print(f"  {'`'+i.rjust(ml)+'`'} from `{ff[i][1]}`")
        case ["ac", path, *args]:
            g = {f"argv{pos}":value for pos, value in enumerate([path, *args])}
            if not isfile(path):
                print(f"The path `{path}` is invalid!")
                exit(1)
            try:
                with open(path, "rb") as file:
                    code = unpack(file.read(), usebar=usebar)
            except:
                print(f"`{path}` cannot be opened!")
                if path.endswith(".mcl"):
                    print(f"Did you mean:\n`mcl.py analyze \"{path}\"" + ((" "+" ".join(map(forms,args))+"`") if args else "`"))
                exit(1)
            try:
                res = parse(code, g, globs=globs)
            except KeyboardInterrupt:
                print("KeyboardInterrupt!")
                res = 0
            if res != 0 and not isinstance(res, tuple):
                print("Error!")
                exit(1)
            _, dv, ff = res
            if dv:
                print("Variables:")
                ml = max(map(len, dv))
                for i in dv:
                    print(f"  {'`'+i.rjust(ml)+'`'}", end="")
                    if i.startswith("-"):
                        print(" - May be used for configs!")
                    else:
                        print()
            if ff:
                print("Subroutines and Labels:")
                ml = max(map(len, ff))
                for i in ff:
                    print(f"  {'`'+i.rjust(ml)+'`'} from `{ff[i][1]}`")
        case ["compile",scr,dest]:
            if not isfile(scr):
                print(f"The path `{path}` is invalid!")
            open(dest,"wb").write(pack(compiler(open(scr).read()),usebar=usebar))
        case ["rc",path,*args]:
            g = {f"argv{pos}":value for pos, value in enumerate([path, *args])}
            if not isfile(path):
                print(f"The path `{path}` is invalid!")
                exit(1)
            try:
                with open(path, "rb") as file:
                    code = unpack(file.read(),usebar=usebar)
            except:
                print(f"`{path}` cannot be opened!")
                if path.endswith(".mcl"):
                    print(f"Did you mean:\n`mcl.py run \"{path}\"" + ((" "+" ".join(map(forms,args))+"`") if args else "`"))
                exit(1)
            try:
                res = parse(code, g, globs=globs)
            except KeyboardInterrupt:
                print("KeyboardInterrupt!")
                res = 0
            if res != 0 and not isinstance(res, tuple):
                print("Error!")
                exit(1)
        case ["globals"]:
            with open(GLOBAL,"rb") as f:
                file = f.read()
                files = len(file)
                data = dill.loads(file)
                if not data:
                    print("[Empty]")
                    exit(0)
                ml = max(map(len, data.keys()))
                print(f"File: {GLOBAL}\nFile size: {files}")
                for name, [module,value] in data.items():
                    print(f"{str(name).rjust(ml)} = {value!r} of type {type(value).__name__}, defined by `{module}`")
        case _:
            print("Unknown command!\nrun [file] - run file\nanalyze [file] - print info\ncompile [source] [result] - compile file\nrc [file] - run compiled file.\nac [file] - Analyze a compiled script.")
            exit(1)
if __name__ == "__main__":
    data = set()
    expected = ["profile","usebar","version","goof","show_memory", "show_memory_advance", "serious"]
    for pos,item in enumerate(argv):
        if pos == 0:
            continue
        if item.startswith("--"):
            data.add(item[2:].replace("-","_"))
        else:
            break
    argv = argv[:1] + argv[pos:]
    for i in expected:
        globals()[i] = i in data
    if version and goof:
        print(VER_GOOF)
        ilibs.easteregg.print_cat()
        exit()
    elif version and serious:
        print(VER_SERIOUS)
        exit()
    elif version:
        print(VER_STR)
        exit()
    if show_memory:
        print("Monitoring memory...")
        main = monitor_memory(main)
    if show_memory_advance:
        print("Monitoring memory...")
        main = monitor_memory_highres(main)
    if profile:
        cProfile.run('main()')
    else:
        main()