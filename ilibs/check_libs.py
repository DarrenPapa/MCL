import os as s


def check_lib(names=("dill","psutil")):
	for i in names:
		try:
			__import__(i)
		except ImportError:
			return i
	return False
