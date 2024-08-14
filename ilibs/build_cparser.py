import info as i, os

name =  i.SYSTEM_NAME

os.system(os.path.join(".", "setup.py build_ext; pause"))

if name == "posix":
	with open("parser.py", "r") as f:
		with open("cparser.pyx", "w") as d:
			d.write(f.read())
elif name == "nt":
	with open("parser.py", "r") as f:
		with open("cparser_win.pyx", "w") as d:
			d.write(f.read())
else:
	print("Incompatible system!")