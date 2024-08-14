import os

for pack in ("dill","psutil"):
	if os.system(f"pip install {pack}"):
		print(f"Problem installing `{pack}`")
