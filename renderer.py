#!/usr/bin/env python3
import os
import sys

LINES = 19

def form(text, dest, cut=45):
    ldest = list(dest)
    for pos, [tc, dc] in enumerate(zip(text, dest)):
        if dc == " ":
            ldest[pos] = tc
        else:
            break
    else:
        return "".join(ldest)[:cut]+" #"
    return text+dest[len(text)][:cut]+" #"

def render(text):
    text = text.split("\n")
    text.append("--===[END]===--")
    p = 0
    title = header = text[0]
    show_long = True
    while p < len(text):
        if p < 0:
            p = 0
        os.system("cls" if os.name == "nt" else "clear")
        comt = text[p].strip()
        if comt.startswith("[") and comt.endswith("]"):
            title = text[p].strip()
        elif comt != "::" and text[p-1] != "%%dont-display" and text[p].rstrip().endswith(":"):
            title, *_ = title.split("-",1)
            title = title.rstrip()
            title += " - " + comt[:-1].strip()
        elif text[p-1].strip() != "%%dont-display" and comt.startswith("==") and comt.endswith("=="):
            title, *_ = title.split(":",1)
            title = title.rstrip()
            title += " : " + comt[2:-2].strip()
        elif comt == "%%no-title":
            title = header
        elif comt == "%%no-section":
            title, *_ = title.split("-",1)
            title = title.rstrip()
        elif comt == "%%no-subsection":
            title, *_ = title.split(":",1)
            title = title.rstrip()
        elif comt == "%%show-long-off":
            show_long = False
        elif comt == "%%show-long-on":
            show_long = True
        print(title)
        for line in text[p:p+LINES]+[""]*(LINES-len(text[p:p+LINES-1])):
            if line.strip().startswith("%%"):
                p += 1
                continue
            if not line.strip():
                print()
                continue
            if show_long and len(line) > 50:
                print(form("[CUT]",line))
            else:
                print(line)
        act = input(f"{p} ]")
        if act == "page":
            p += LINES
        elif act == "rpage":
            p -= LINES
        elif act == "lines":
            input(f"{len(text):,}\nPress Enter")
        elif act == "setline":
            while True:
                act = input("Number: ")
                if act.isdigit():
                    if int(act) < len(text):
                        p = int(act)
                        while text[p].strip().startswith("%%") and p > 0 and p < len(text):
                            p += 1
                        break
                    else:
                        input(f"Out of bounds!\nPress Enter")
                else:
                    input(f"Not a number!\nPress Enter")
        elif act == "forward":
            while True:
                act = input("Number: ")
                if act.isdigit():
                    if int(act)+p < len(text):
                        p += int(act)
                        while text[p].strip().startswith("%%") and p > 0 and p < len(text):
                            p += 1
                        break
                    else:
                        input(f"Out of bounds!\nPress Enter")
                else:
                    input(f"Not a number!\nPress Enter")
        elif act == "backward":
            while True:
                act = input("Number: ")
                if act.isdigit():
                    p -= int(act)
                    while text[p].strip().startswith("%%") and p > 0 and p < len(text):
                        p -= 1
                    break
                else:
                    input(f"Not a number!\nPress Enter")
        elif act == "seekline":
            while True:
                act = input("Number: ")
                if act.isdigit():
                    if int(act) < len(text):
                        input(text[int(act)]+"\n\nPress Enter")
                    else:
                        input(f"Out of bounds!\nPress Enter")
                else:
                    input(f"Not a number!\nPress Enter")
        elif act == "r":
            p -= 1
            while text[p].strip().startswith("%%") and p > 0 and p < len(text):
                p -= 1
            continue
        elif act == "home":
            p = 0
            continue
        elif act == "end":
            p = len(text)-1
            continue
        elif act == "quit":
            break
        p += 1

if len(sys.argv) == 2:
    if os.path.isfile(sys.argv[1]):
        render(open(sys.argv[1]).read())
    else:
        print("Invalid path!")
else:
    print("Usage: renderer.py [file]")
    huh