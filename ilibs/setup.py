from setuptools import setup, Extension
from Cython.Build import cythonize
from traceback import format_exc
from info import SYSTEM_NAME as name

try:
    ext_modules = [
        Extension(
            "cparser" if name == "posix" else "cparser_win",  # Name of the module
            sources=["cparser" if name == "posix" else "cparser_win"],  # Cython source file
        )
    ]

    setup(
        ext_modules=cythonize(ext_modules)
    )
except:
    print(format_exc())
input()