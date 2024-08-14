# Do not modify carelessly
# This is used by mcl.py to do
# execution, packing, unpacking and compiling
# of scripts.

# HANDLE WITH INTENSE CARE

# Contributors:
#     Darren Chase Papa

# DEPRECATION WARNING FOR "includepy"

import dill
import traceback
import __main__
from os.path import isfile, isdir, basename, dirname, join
from sys import argv
from . import loadutils, info
from .info import *

string = {
    "\\\\":chr(300),
    "\\n":"\n",
    "\\s":"\s",
    "\\t":"\t",
    "\\r":"\r",
    "\\b":"\b",
    "\\v":"\v",
    "\\f":"\f",
    "\\%":"§",   # For formatting
    "\\[goof]":"why?",
    "\\[mn]":"\r\n",  # microsoft newline?
    chr(300):"\\"
}

def define(name, value):
    return ("set", name, value)

def defineg(name, value):
    return ("gset", name, value)

def error(message):
    return ("error", message)

def rexit():
    return ("exit",)

def includepy(path, use_object=False):
    data = {
        "getcore":lambda x: includepy(join(INTERP, x), True),
        "getlibs":lambda x: includepy(join(LIBDIR, x), True),
        "info":info,
        "nil":"0",
        "none":0,
        "true":1,
        "false":0,
        "LIBDIR":LIBDIR,
        "BINDIR":BINDIR,
        "INTERP":INTERP,
        "VERSION":VERSION,
        "define":define,
        "error":error,
        "rexit":rexit,
        "defineg":defineg,
        "log":lambda text: print(f"{path}: {text}"),
        "__name__":"mcl-inter",
        "__builtins__":__main__.__builtins__.__dict__.copy()
    }
    data["__builtins__"]["__import__"] = lambda *x, **y: None
    data["__builtins__"]["open"] = lambda *x, **y: None
    with open(path) as f:
        try:
            exec(compile(f.read(),"script","exec"), data)
        except:
            try:
                if not USE_IL_FALLBACK:
                    raise
                print("WARNING: IGNORED ERROR")
                return None, {}
            except:
                print("Error while including a python script!\nFile:",path)
                exit(1)
    fd = {}
    mn = data.get("MODULE_NAME", basename(path).split(".")[0])
    for n, d in data.items():
        if n.startswith("_") or n in ("sys","MODULE_NAME", "DATA"):
            continue
        elif n.startswith("m_"):
            name = mn + ":" + n[2:]
            fd[name] = d
        elif hasattr(d, "__path__") or hasattr(d, "__file__"):
            continue
        else:
            fd[n] = d
    if use_object:
        return type(f"module:<{mn}>", (object,), fd)
    return mn, fd

def identifier(name):
    for i in name.split("-"):
        if i.startswith('"') and i.endswith('"'):
            continue
        elif i == "$input":
            continue
        elif i.startswith(".") and i[1:].replace("_","").isalnum():
            continue
        elif not i.replace("_","").isalnum():
            return False
    return True

# Self explanatory
def compiler(code, LIBDIR=LIBDIR):
    r = []
    func = {
        "%modules":[]
    }
    psuedo = {}       # hold constants values
    noop = False      # no optimize
    nocw = False      # no compiler warning
    ml = None         # Multi line comment name
    md = None         # Doc name
    name = None       # Variable
    temp = []         # Documentation line buffer
    docs = {}         # Docs
    symtable = set()  # Symtable
    nsymtable = set() # Symtable
    nendl = False     # ignore the first nendl to encounter
    zloop = False     # remove the first loop body (including the loop)
    arch = False      # easter egg
    print_code = False
    for pos,line in enumerate([line.strip() for line in code.split("\n")],1):
        if line == "**>" and ml is not None:
            ml = None
            continue
        elif line == "doc>" and md is not None:
            docs[md] = "\n".join(temp)
            md = None
            temp.clear()
            continue
        elif ml is not None:
            continue
        elif md is not None:
            line = "  "+line
            temp.append(line)
            continue
        elif line.startswith("*") or not line:
            continue
        elif line.startswith("<** "):
            name = line[4:].strip()
            ml = name
        elif line.startswith("<doc "):
            name = line[5:].strip()
            d = f"Documentation for {name}"
            temp.append(d)
            md = name
        elif line.startswith("!"):
            inc, value = line[1:].split(" ",1) if " " in line[1:] else (line[1:],None)
            if inc == "include" and value is not None:
                if value.startswith("<") and value.endswith(">"):
                    ov = value
                    value = join(LIBDIR, value[1:-1])
                    if not isfile(value):
                        print(f"Error [line {pos}]: File not found in libs:\n{ov}")
                        exit(1)
                    try:
                        d, ff, rr = compiler(open(value).read(), LIBDIR)
                    except RecursionError:
                        print(f"[Curcular include]\nLine {pos}")
                        exit(1)
                    r.extend(rr)
                    docs.update(d)
                else:
                    if not isfile(value):
                        print(f"Error [line {pos}]: File not found:\n{value}")
                        exit(1)
                    try:
                        d, ff, rr = compiler(open(value).read(), LIBDIR)
                    except RecursionError:
                        print(f"[Curcular include]\nLine {pos}")
                        exit(1)
                    r.extend(rr)
                    docs.update(d)
#           DEPRECATED (maybe but soon)
            elif inc == "pyimport" and value is not None:
                if value.startswith("<") and value.endswith(">"):
                    ov = value[1:-1]
                    value = join(LIBDIR, value[1:-1])
                    if not isfile(value):
                        print(f"Error [line {pos}]: File not found in libs:\n{ov}")
                        exit(1)
                    mn, ff = includepy(value)
                    if mn and mn not in func["%modules"]:
                        func["%modules"].append(mn)
                    func.update(ff)
                else:
                    if not isfile(value):
                        print(f"Error [line {pos}]: File not found:\n{value}")
                        exit(1)
                    mn, ff = includepy(value)
                    if mn and mn not in func["%modules"]:
                        func["%modules"].append(mn)
                    func.update(ff)
            elif inc == "includec" and value is not None:
                if value.startswith("<") and value.endswith(">"):
                    ov = value
                    value = join(LIBDIR, value[1:-1])
                    if not isfile(value):
                        print(f"Error [line {pos}]: File not found in libs:\n{ov}")
                    try:
                        try:
                            d, ff, rr = compiler(open(value).read(), LIBDIR)
                        except RecursionError:
                            print(f"[Curcular include]\nLine {pos}")
                            exit(1)
                    except:
                        print("File is a invalid script!")
                else:
                    if not isfile(value):
                        print(f"Error [line {pos}]: File not found:\n{value}")
                        exit(1)
                    try:
                        try:
                            d, ff, rr = compiler(open(value).read(), LIBDIR)
                        except RecursionError:
                            print(f"[Curcular include]\nLine {pos}")
                            exit(1)
                    except:
                        print("File is a invalid script!")
            elif inc == "dontOptimize" and value is None:
                noop = True
            elif inc == "optimize" and value is None:
                noop = False
            elif inc == "printCode" and value is None:
                print_code = True
            elif inc == "noPrintCode" and value is None:
                print_code = False
            elif inc == "hideWarnings" and value is None:
                nocw = True
            elif inc == "clearDocs" and value is None:
                docs = {}
            elif inc == "showWarnings" and value is None:
                nocw = False
            elif inc == "warning" and value is not None:
                if not nocw:
                    print(f"Compiler Warning [raised]: {value}")
            elif inc == "IUseArchBTW" and value is None:
                arch = True
            else:
                print(f"Error [line {pos}]: Invalid instruction: {inc}")
                exit(1)
        else:
            op, arg = line.split(maxsplit=1) if " " in line else (line, None)
            is_dep = True
            if isinstance(arg, str):
                arg = arg.lstrip()
                if arg.startswith("number[") and arg.endswith("]"):
                    try:
                        arg = int(arg[7:-1])
                    except:
                        try:
                            arg = float(arg[7:-1])
                        except:
                            arg = 0
                elif arg.startswith('"') and arg.endswith('"') and len(arg) > 1:
                    for name, text in string.items():
                        arg = arg.replace(name,text)
                elif arg.startswith('<') and arg.endswith('>') and len(arg) > 1:
                    arg = arg[1:-1]
                elif (arg and (arg[0] in ":.?!@")) and identifier(arg[1:]):
                    pass
                elif identifier(arg):
                    pass
                elif arg == "$true":
                    arg = 1
                elif arg == "$false" or arg == "$nil":
                    arg = 0
                elif arg == "$noarg":
                    arg = None
                elif arg == "$input":
                    pass
                elif arg == "$system-name":
                    arg = f'{SYSTEM_NAME!r}'
                elif arg == "$system-build-name":
                    arg = f'{SYSTEM_BUILD_NAME if not arch else "Arch Linux"!r}'
                elif arg == "$interpreter-version":
                    arg = f'{VERSION!r}'
                elif arg == "$system-architecture":
                    arg = f'{SYSTEM_ARCH!r}'
                elif arg == "$?-my-love":
                    arg = "Mary Angel Lariel O. Avena"
                elif arg.startswith("+") and "[" in arg and arg.endswith("]"):
                    pass
                elif arg == "dict[]":
                    arg = {}
                elif arg.startswith("[") and arg.endswith("]") and identifier(arg[1:-1]):
                    pass
                else:
                    arg = "0"
            if not noop:
                ## MECHANISM TO DETECT NON NEEDED LOOPS ON COMPILE TIME ##
                if zloop and op != "endl":
                    continue
                elif zloop and op == "endl":
                    zloop = False
                    continue
                if op == "define" and arg is not None:
                    name = arg
                    r.append((pos,(op,arg,line)))
                elif op == "set" and arg is not None:
                    if name:
                        if isinstance(arg,str) and arg.startswith(".") and arg[1:] in psuedo:
                            psuedo[name] = psuedo[arg[1:]]
                        else:
                            psuedo[name] = arg
                    r.append((pos,(op,arg,line)))
                elif op == "loop" and arg is not None:
                    oarg = arg
                    if isinstance(arg, (float, int)):
                        pass
                    elif arg.startswith(".") and arg[1:] in psuedo:
                        arg = psuedo[arg[1:]]
                    try:
                        arg = int(arg)
                    except ValueError:
                        arg = 2
                    if arg+1 == 1:
                        if not nocw:
                            print(f"Compile Warning: Loop only loops once line {pos}\nLoop was removed due to the loop value being set to 1.")
                        nendl = True
                    elif arg+1 == 0:
                        if not nocw:
                            print(f"Compile Warning: Loop excempted at line {pos}\nCode was removed to optimize runtime.\nLoop was set to 0.")
                        zloop = True
                    else:
                        r.append((pos,(op,oarg,line)))
                elif op == "xloop" and arg is not None:
                    oarg = arg
                    if isinstance(arg, (float, int)):
                        pass
                    elif arg.startswith(".") and arg[1:] in psuedo:
                        arg = psuedo[arg[1:]]
                    try:
                        arg = int(arg)
                    except ValueError:
                        arg = 2
                    if arg == 1:
                        if not nocw:
                            print(f"Compile Warning: Loop only loops once line {pos}\nLoop was removed due to the loop value being set to 1.")
                        nendl = True
                    elif arg == 0:
                        if not nocw:
                            print(f"Compile Warning: Loop excempted at line {pos}\nCode was removed to optimize runtime.\nLoop was set to 0.")
                        zloop = True
                    else:
                        r.append((pos,(op,oarg,line)))
                elif op == "endl" and nendl:
                    nendl = False
                else:
                    r.append((pos,(op,arg,line)))
            else:
                r.append((pos,(op,arg,line)))
    else:
        if ml:
            print(f"Comment `{ml}` not closed!")
            exit(1)
        if md:
            print(f"Documenttion for `{md}` not closed!")
            exit(1)
    r = tuple(r)
    if not noop:
        ## SYMBOL PROCESSING ##
        # removes unnecessary subroutines and labels
        # first pass
        rrr = []
        for index,[pos, [op, arg, line]] in enumerate(r):
            if op == "call" and arg is not None:
                symtable.add(arg.strip())
            elif op == "goto" and arg is not None:
                symtable.add(arg)
            elif op.startswith("if") and op[-2:] in ("eq","ne","lt","gt") and len(op) == 4 and arg is not None:
                symtable.add(arg)
            elif op == "_proto" and arg is not None:
                name, uname = arg.split("->") if "->" in arg else (arg, None)
                name = name.strip()
                if uname:
                    uname = uname.strip()
                    nsymtable.add(uname)
                    symtable.add(uname)
                    nsymtable.add(name)
                symtable.add(name)
                continue
            rrr.append((pos,(op,arg,line)))
        # second pass
        rr = []
        nends = False
        for index,[pos, [op, arg, line]] in enumerate(rrr):
            if nends and op != "ends":
                continue
            elif nends and op == "ends":
                nends = False
                continue
            if op == "subroutine" and arg is not None:
                name = arg.strip()
                if name not in nsymtable:
                    nsymtable.add(name)
                else:
                    if not nocw:
                        print(f"Compile Warning:\nA subroutine may have been defined twice!\nName: {name}\nLine {pos}")
                if name in symtable:
                    symtable.remove(name)
                else:
                    if not nocw:
                        print(f"Compile Warning: Subroutine `{name}` not used.\nRemoved since it isnt called.\nLine {pos}")
                    nends = True
                    continue
            elif op == "label" and arg is not None:
                name = arg
                if name not in nsymtable:
                    nsymtable.add(name)
                else:
                    if not nocw:
                        print(f"Compile Warning:\nA label may have been defined twice!\nName: {name}\nLine {pos}")
                if arg in symtable:
                    symtable.remove(arg)
                else:
                    if not nocw:
                        print(f"Compile Warning: Label `{name}` not used.\nRemoved since it does nothing. If that is your intention use `pass`\nLine {pos}")
                    continue
                nsymtable.add(name)
            rr.append((pos,(op,arg,line)))
        if print_code:
            print("Code:")
            if rr:
                ml = len(str(max(map(lambda x:x[0], rr))))+1
            for lp, [_, _, c] in rr:
                print(f"{str(lp).zfill(ml)}  "+c)
            print()
        for name in symtable:
            if name not in nsymtable:
                print(f"Compile Error: Undefined subroutine or label `{name}`\nLine {pos}")
                exit(1)
        rrr = []
        p = 0
        pr = len(rr)
        while p < pr:
            pos, [op, arg, line] = rr[p]
            if op == "loop" and p+1 < pr and rr[p+1][1][0] == "endl":
                if not nocw:
                    print(f"Compile Warning: Loop does nothing on line {pos}\nThe loop was removed to increase speed.")
                p += 2
                continue
            elif op == "xloop" and p+1 < pr and rr[p+1][1][0] == "endl":
                if not nocw:
                    print(f"Compile Warning: Loop does nothing on line {pos}\nThe loop was removed to increase speed.")
                p += 2
                continue
            else:
                rrr.append((pos, (op, arg, line)))
            p += 1
        return docs, func, rrr
    else:
        if print_code:
            print("Code:")
            if r:
                ml = len(str(max(map(lambda x:x[0], r))))+1
            for lp, [_, _, c] in r:
                print(f"{str(lp).zfill(ml)}  "+c)
            print()
        return docs, func, r

# Packs code given by compile
# This removes argument duplicates
# Also removes operation duplicates
# Repeated values are compressed into one and
# is turned into indexes to be unpacled later.
def pack(code, pickle=True, usebar=False):
    docs, func, code = code
    r = []
    st = []
    def getindex(v):
        if v not in st:
            st.append(v)
            return len(st)-1
        else:
            return st.index(v)
    for pos, [op, arg, line] in code if not usebar else loadutils.iterbar(code,task="Packing"):
        r.append((pos,getindex(op),getindex(arg),getindex(line)))
    res = {
        "func":func,
        "docs":docs,
        "vals":tuple(st),
        "code":r
    }
    return dill.dumps(res) if pickle else res

# Unpacks the bytecode from a bytes object
def unpack(code, pickle=True, usebar=False):
    code = dill.loads(code) if pickle else code
    func, docs = code["func"], code["docs"]
    vals = code["vals"]
    res = []
    for line, op, arg, linestr in code["code"] if not usebar else loadutils.iterbar(code["code"],task="Unpacking"):
        res.append((line,(vals[op],vals[arg],vals[linestr])))
    return docs, func, tuple(res)

# Prints the bytecode in a human readable format
# Format: line - op_index -> op_name arg_index -> arg_value
def deconstruct(code):
    vals = code["vals"]
    code = code["code"]
    ml = len(str(max(map(lambda x:x[0], code))))
    mlo = len(str(max(map(lambda x:x[1], code))))
    mla = len(str(max(map(lambda x:x[2], code))))
    ops = map(lambda x: vals[x[1]], code)
    mlos = max(map(len, ops))
    for line, op, arg, _ in code:
        print(f"{str(line).zfill(ml)} - {str(op).zfill(mlo)} -> {str(vals[op].center(mlos)).zfill(mla)} {arg} -> {vals[arg]!r}")