# cython: language_level=3
# cython: optimize.use_switch=True

# NOTE cparser.cpython-311.so IS NOT YET AVAILABLE

# the lines above is for cparser.pyx do not remove

# Do not modify carelessly
# This is used by mcl.py to do
# execution and parsing of scripts.

# HANDLE WITH INTENSE CARE

# Contributors:
#     Darren Chase Papa

from . import compiler, info
import time, dill, gc

def getindex(code,cur,item):
    TEMP_CODE = list(map(lambda x: x[1][0], code))[cur:]
    if item not in TEMP_CODE:
        return -1
    else:
        return TEMP_CODE.index(item)+cur

def clean():
    open(info.GLOBAL, "wb").write(dill.dumps(globsu))

def getvar(data, name, default="0", sep="-"):
    node = data
    names = name.split(sep)
    for pos,name in enumerate(names):
        if name.startswith('"') and name.endswith('"'):
            name = name[1:-1]
        elif name == "$input":
            name = input()
        elif name.startswith("."):
            name = data.get(name[1:], "0")
        if name in node and isinstance(node[name], dict) and pos != len(names)-1:
            node = node[name]
        elif name in node and pos == len(names)-1:
            return node[name]
        else:
            return default
    return default

def popvar(data, name, default="0", sep="-"):
    node = data
    names = name.split(sep)
    for pos,name in enumerate(names):
        if name.startswith('"') and name.endswith('"'):
            name = name[1:-1]
        elif name == "$input":
            name = input()
        elif name.startswith("."):
            name = data.get(name[1:], "0")
        if name in node and isinstance(node[name], dict) and pos != len(names)-1:
            node = node[name]
        elif name in node and pos == len(names)-1:
            return node.pop(name)
        else:
            return default
    return default

def setvar(data, name, value, sep="-"):
    node = data
    names = name.split(sep)
    for pos,name in enumerate(names):
        if name.startswith('"') and name.endswith('"'):
            name = name[1:-1]
        elif name == "$input":
            name = input()
        elif name.startswith("."):
            name = data.get(name[1:], "0")
        if name in node and isinstance(node[name], dict) and pos != len(names)-1:
            node = node[name]
        elif name and pos == len(names)-1:
            node[name] = value

def nameexpr(data, name, sep="-"):
    res = []
    names = name.split(sep)
    for pos,name in enumerate(names):
        if name.startswith('"') and name.endswith('"'):
            name = name[1:-1]
        elif name == "$input":
            name = input()
        elif name.startswith("."):
            name = data.get(name[1:], "0")
        res.append(name)
    return sep.join(res)

def action(action, locals, globals):
    op, *args = action
    argc = len(args)
    if op == "set" and argc == 2:
        locals[args[0]] = args[1]
    elif op == "gset" and argc == 2:
        globals[args[0]] = args[1]
    elif op == "error" and argc == 1:
        return ("error",args[0])
    elif op == "error" and argc == 0:
        return ("error",)
    elif op == "goto" and argc == 1:
        return ("goto", args[0])
    elif op == "exit" and argc == 0:
        clear()
        exit()

def call(function, state):
    res = function(state)
    if res is None:
        return
    elif not isinstance(res, tuple):
        return
    try:
        return action(res, state.locals, state.globals)
    except (SystemExit, KeyboardInterrupt):
        action(("exit",), None, None)
    except Exception as e:
        return ("error",repr(e))

def parse(code, analyze=True, globs=None, max_scope=None, data=None):
    gc.disable()
    global globsu
    docs, func, code = compiler.compiler(code) if isinstance(code, str) else code
    for name,v in docs.items():
        print(v)
    data = [{}] if data is None else data
    # global data scope
    gd = data[0]
    # local data scope (global is default)
    ld = data[-1]
    # persistant global storage
    globs = globs if globs is not None else {}
    # to be able to set globs to the global scope
    globsu = globs
    # helper function to make a new scope
    def newscope():
        if max_scope is not None and len(data)+1 > max_scope:
            print("Runtime Warning: Exceeding set max scopes!")
        nonlocal ld
        data.append({})
        ld = data[-1]
    # helper function to remove a scope
    def popscope():
        if len(data) < 2:
            print(f"Error in line {pos}\nInvalid popscope!")
            exit(1)
        nonlocal ld
        data.pop()
        ld = data[-1]
    # switch to global context
    def useglobal():
        nonlocal ld
        ld = gd
    # switch to local context
    def uselocal():
        nonlocal ld
        ld = data[-1]
    p = 0 # index (keeps track of the current instruction)
    # name: iter, module, line, return variable
    # iter - for loops
    # module - info and debugging
    # line - line of the caller (index)
    # return variable - for the callee specified by the caller
    ret = [] # keeps track of return positions
    # name: module, line
    # module - info and debugging
    # line - line of the destination (index)
    jumps = {} # the dict to store labels and subroutines
    name = None # current open name
    op1 = op2 = None # used for comparisons (used by set1 and set2)
    module = "main" # debug info
    ptime = 0.0 # used by %START, %END and %OUTTIME
    text = [] # Used for multilines
    while p < len(code):
        pos, [op, arg, line] = code[p]
        if not isinstance(arg, str):
            pass
        elif arg.startswith("."):
            arg = getvar(ld, arg[1:])
        elif arg.startswith("!"):
            arg = getvar(gd, arg[1:])
        elif arg.startswith(":"):
            arg = getvar(ld, arg[1:], getvar(ld, arg[1:]))
        elif arg.startswith("@"):
            arg = getvar(ld, getvar(ld, arg[1:], None), None)
            if arg is None:
                arg = getvar(gd, getvar(ld, arg[1:]))
        elif arg.startswith("?"):
            arg = 1 if getvar(ld, arg[1:], getvar(gd, arg[1:], None)) is not None else 0
        elif arg.startswith('"') and arg.endswith('"') or arg.startswith("'") and arg.endswith("'"):
            arg = arg[1:-1]
        elif arg == "$input":
            arg = input()
        elif arg.startswith("[") and arg.endswith("]"):
            arg = nameexpr(ld, arg[1:-1])
        elif arg.startswith("&") and "[" in arg and arg.endswith("]"):
            name, index = arg[1:-1].split("[")
            nlist = ld.get(name,gd.get(name))
            if not isinstance(nlist,(tuple,list,str)):
                print(f"`{name}` is not valid!")
                break
            if index.isdigit():
                index = int(index)
            elif index.startswith("."):
                index = getvar(ld, index[1:], getvar(gd, index[1:], 0))
            if not isinstance(index,int):
                print(f"Index `{index}` of type `{type(index).__name__}` is invalid!")
                break
            if index not in range(len(nlist)):
                print(f"Index `{index}` is out of bounds!")
            arg = nlist[index]
        elif compiler.identifier(arg):
            pass
        else:
            arg = "0"
        if op == "pass":
            pass
        elif op == "program" and arg is not None:
            module = arg
        elif op == "getlen" and arg is not None:
            if name is None:
                print("No open name!")
                break
            if arg not in ld:
                print(f"`{arg}` is undefined!")
                break
            ld[name] = len(ld[arg])
        elif op == "print":
            if arg is not None:
                print(arg,end="")
        elif op == "println":
            if arg is not None:
                print(arg)
            else:
                print()
        elif op == "define" and arg is not None:
            name = arg
        elif op == "close" and arg is None:
            name = None
        elif op == "set" and arg is not None:
            if name is None:
                print("No open name!")
                break
            setvar(ld, name, arg)
            name = None
        elif op == "gset" and arg is not None:
            if name is None:
                print("No open name!")
                break
            setvar(gd, name, arg)
            name = None
        elif op == "list" and arg is not None:
            if name is None:
                print("No open name!")
                break
            setvar(ld, name, [0]*arg)
        elif op == "getnonlocal" and arg is not None:
            if name is None:
                print("No open name!")
                break
            if len(data) > 1:
                setvar(ld, name, getvar(data[-2], arg))
            else:
                print("No scope to get it from!")
                break
        elif op == "getlocal" and arg is not None:
            if name is None:
                print("No open name!")
                break
            setvar(ld, name, getvar(ld, arg))
        elif op == "getglobal" and arg is not None:
            if name is None:
                print("No open name!")
                break
            setvar(ld, name, getvar(gd, arg))
        elif op == "delete" and arg is not None:
            popvar(ld, arg)
        elif op == "deleteglobal" and arg is not None:
            popvar(gd, arg)
        elif op == "format" and arg is not None:
            if name is None:
                print("No open name!")
                break
            text = arg
            for n, value in ld.items():
                text = text.replace(f"§{n}§", str(value))
            ld[name] = text
            name = None
        elif op == "%START" and arg is None:
            ptime = time.time()
        elif op == "%END" and arg is None:
            ptime = time.time() - ptime
        elif op == "%OUTTIME" and arg is None:
            print(f"\nBuilt-in Timer\nTime Elapsed: {ptime:,.8f}s\n")
        elif op == "%GETTIME" and arg is not None:
            setvar(ld, arg, ptime)
        elif op == "%GETUNIXTIME" and arg is not None:
            setvar(ld, arg, time.time())
        elif op == ".useGlobal" and arg is None:
            useglobal()
        elif op == ".useLocal" and arg is None:
            uselocal()
        elif op == ".globalset" and arg is not None:
            if name is None:
                print("No open name!")
                break
            globs[name] = arg
            name = None
        elif op == ".globalget" and arg is not None:
            if name is None:
                print("No open name!")
                break
            if name not in globs:
                print(f"`{name}` is not defined in the globals!")
            ld[arg] = globs[name]
            name = None
        elif op == ".inglobal" and arg is not None:
            if arg not in jumps:
                print(f"`{arg}` is not defined!")
                break
            if name is None:
                print("No open name!")
                break
            if name in globs:
                ret.append([None, module, p, name])
                module, p = jumps[arg]
            name = None
        elif op == ".notinglobal" and arg is not None:
            if arg not in jumps:
                print(f"`{arg}` is not defined!")
                break
            if name is None:
                print("No open name!")
                break
            if name not in globs:
                ret.append([None, module, p, name])
                module, p = jumps[arg]
            name = None
        elif op == "[" or op == ".newScope" and arg is None:
            newscope()
        elif op == "]" or op == ".endScope" and arg is None:
            popscope()
        elif op == "subroutine" and arg is not None:
            jumps[arg] = (module, p)
            p = getindex(code, p, "ends")
            if p == -1:
                print("Invalid subroutine!")
                break
        elif op == "label" and arg is not None:
            jumps[arg] = (module, p)
        elif op == "call" and arg is not None:
            if arg not in jumps:
                print(f"`{arg}` is not defined!")
                break
            ret.append([None, module, p, name])
            module, p = jumps[arg]
            name = None
        elif op == ".push_frame":
            ret.append([None, module, p, arg])
        elif op == "goto" and arg is not None:
            if arg not in jumps:
                print(f"`{arg}` is not defined!")
                break
            module, p = jumps[arg]
        elif op == "return":
            if not ret:
                print("Invalid return statement!")
                break
            _, module, p, n = ret.pop()
            if n is not None and arg is not None:
                if len(data) > 1:
                    data[-2][n] = arg
                else:
                    gd[n] = arg
        elif op == "give":
            if not ret:
                print("Invalid give statement!")
                break
            _, _, _, n = ret[-1]
            if n is not None and arg is not None:
                if len(data) > 1:
                    data[-2][n] = arg
                else:
                    gd[n] = arg
        elif op == "loop" and arg is not None:
            ret.append([int(arg), module, p])
        elif op == "xloop" and arg is not None:
            ret.append([int(arg)-1, module, p, None])
        elif op == "endl" and arg is None:
            if not ret:
                print("No loops to iterate!")
                break
            if ret[-1][0] != None:
                if ret[-1][0] == 0:
                    ret.pop()
                else:
                    ret[-1][0] -= 1
                    p = ret[-1][2]
            else:
                pass
        elif op == "exit" and arg is None:
            return 0
        elif op == "set1" and arg is not None:
            op1 = arg
        elif op == "set2" and arg is not None:
            op2 = arg
        elif op == "ifeq" and arg is not None:
            if arg not in jumps:
                print(f"`{arg}` is not defined!")
                break
            if op1 is None or op2 is None:
                print("the if statements operators are not set!")
                break
            if op1 == op2:
                ret.append([None, module, p, name])
                module, p = jumps[arg]
            name = None
        elif op == "ifne" and arg is not None:
            if arg not in jumps:
                print(f"`{arg}` is not defined!")
                break
            if op1 is None or op2 is None:
                print("the if statements operators are not set!")
                break
            if op1 != op2:
                ret.append([None, module, p, name])
                module, p = jumps[arg]
            name = None
        elif op == "ifgt" and arg is not None:
            if arg not in jumps:
                print(f"`{arg}` is not defined!")
                break
            if op1 is None or op2 is None:
                print("the if statements operators are not set!")
                break
            if op1 >= op2:
                ret.append([None, module, p, name])
                module, p = jumps[arg]
            name = None
        elif op == "iflt" and arg is not None:
            if arg not in jumps:
                print(f"`{arg}` is not defined!")
                break
            if op1 is None or op2 is None:
                print("the if statements operators are not set!")
                break
            if op1 == op2:
                ret.append([None, module, p, name])
                module, p = jumps[arg]
            name = None
        elif op == "cast" and arg is not None:
            if arg not in ("int","float","str"):
                print("Invalid type!")
                break
            if name is None:
                print("No open name!")
                break
            if name not in ld:
                print(f"`{name}` is not defined!")
                break
            try:
                ld[name] = getattr(__builtins__,arg)(ld[name])
            except:
                print("Invalid cast!")
                break
        elif op == "add" and arg is not None:
            if name is None:
                print("No open name!")
                break
            if name not in ld:
                print(f"`{name}` is not defined!")
                break
            ld[name] += arg
        elif op == "sub" and arg is not None:
            if name is None:
                print("No open name!")
                break
            if name not in ld:
                print(f"`{name}` is not defined!")
                break
            ld[name] -= arg
        elif op == "mul" and arg is not None:
            if name is None:
                print("No open name!")
                break
            if name not in ld:
                print(f"`{name}` is not defined!")
                break
            ld[name] *= arg
        elif op == "div" and arg is not None:
            if name is None:
                print("No open name!")
                break
            if name not in ld:
                print(f"`{name}` is not defined!")
                break
            ld[name] /= arg
        elif op == "mod" and arg is not None:
            if name is None:
                print("No open name!")
                break
            if name not in ld:
                print(f"`{name}` is not defined!")
                break
            ld[name] %= arg
        elif op == "newstring" and arg is None:
            text = []
        elif op == ">" and arg is not None:
            text.append(arg)
        elif op == "string" and arg is not None:
            ld[arg] = "\n".join(text)
        elif op.endswith("++") and arg is None:
            v = getvar(ld, op[:-2], None)
            if v is not None:
                setvar(ld, op[:-2], v+1)
            else:
                v = getvar(gd, op[:-2], None)
                if v is not None:
                    setvar(gd, op[:-2], v+1)
                else:
                    print(f"`{op[:-2]}` is not defined!")
        elif op.endswith("--") and arg is None:
            v = getvar(ld, op[:-2], None)
            if v is not None:
                setvar(ld, op[:-2], v-1)
            else:
                v = getvar(gd, op[:-2], None)
                if v is not None:
                    setvar(gd, op[:-2], v-1)
                else:
                    print(f"`{op[:-2]}` is not defined!")
        elif op.startswith("#") and op[1:] in func:
            r = call(func[op[1:]],type("state", (object,),
                {
                    "arg":arg,
                    "name":name,
                    "locals":ld,
                    "globals":gd,
                    "functions":func,
                    "data":data,
                    "globals_index":0,
                    "local_index":-1,
                    "nonlocals_index":-2,
                    "current_index":p,
                    "current_line":pos,
                    "modules":type("modules", (object,), func)
                }
            ))
            if r is None:
                p += 1
                continue
            r, *ags = r
            agc = len(ags)
            if r == "error" and agc:
                print(agc[0])
                break
            elif r == "error":
                break
            elif r == "goto" and agc:
                p = agc[0]
        else:
            if name is None:
                print("No open name!")
                break
            print(f"Invalid operation: {op}")
            break
        p += 1
    else:
        clean();gc.enable()
        return 0
    print(f"\n== Runtime Error ==\nIn module `{module}`\nLine: {line}\nLine number {pos}")
    clean();gc.enable()
    return 1