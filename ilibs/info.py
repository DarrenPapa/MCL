# Do not modify carelessly
# This is used by mcl.py to get system info
# This is very platform DEPENDENT

# HANDLE WITH INTENSE CARE

# Contributors:
#     Darren Chase Papa

from os import name, path
from sys import argv
from platform import uname
__all__ = ["VERSION","SYSTEM_NAME","SYSTEM_ARCH","SYSTEM_BUILD_NAME","LIBDIR","BINDIR","GLOBAL","SUPORTED","ISSUPORTED","INTERP","system_info_str"]
VERSION = "0.1-a"
SYSTEM_NAME = name
SYSTEM_ARCH = uname().machine
SYSTEM_BUILD_NAME = uname().system
BINDIR = path.dirname(argv[0])
LIBDIR = path.join(BINDIR, "libs")
INTERP = path.join(BINDIR, "ilibs")
GLOBAL = path.join(LIBDIR, "global.pkl")
SUPORTED = ("nt","posix")
ISSUPORTED = SYSTEM_NAME.lower() in SUPORTED
system_info_str = f"""[System Info]
System Kernel: {SYSTEM_NAME}
 System Build: {SYSTEM_BUILD_NAME}
  System Arch: {SYSTEM_ARCH}
[Interpreter Info]
Inter Version: {VERSION}
  Interpreter: {BINDIR}
     MCL Libs: {LIBDIR}
MCL Core Path: {INTERP}"""

if __name__ == "__main__":
    print(system_info_str)