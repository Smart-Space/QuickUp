"""
Build script for the QuickUp C++ extension module (QUmodule.pyd).
"""
import os
import sys
from setuptools import setup, Extension


MODULE_NAME = "QUmodule"
SOURCE_FILE = "QUmodule.cpp"
INCLUDE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))


def _detect_python_info():
    """Locate the active Python include/lib directories for the MSVC toolchain."""
    py_version = sys.version_info
    version_tag = f"{py_version.major}{py_version.minor}"

    candidates = [
        sys.prefix,
        os.path.dirname(sys.executable),
    ]
    for root in candidates:
        include = os.path.join(root, "include")
        libs = os.path.join(root, "libs")
        if os.path.isdir(include) and os.path.isdir(libs):
            return include, libs, version_tag


def _normalize_windows_path(path):
    return path.replace("/", os.sep)

include_dir, libs_dir, version_tag = _detect_python_info()
python_lib = os.path.join(libs_dir, f"python{version_tag}.lib")

system_libs = [
    "advapi32",
    "ole32",
    "user32",
    "shell32",
    "comctl32",
    "dwmapi",
]

extra_compile_args = ["/std:c++20", "/utf-8", "/O2", "/DNDEBUG", "/EHsc"]
extra_link_args = ["/LTCG"]

module = Extension(
    name=MODULE_NAME,
    sources=[SOURCE_FILE],
    include_dirs=[_normalize_windows_path(include_dir)],
    libraries=[f"python{version_tag}"] + system_libs,
    library_dirs=[_normalize_windows_path(libs_dir)],
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args,
    define_macros=[("NDEBUG", None)],
)


setup(
    name=MODULE_NAME,
    version="1.0.0",
    description="QuickUp C++ extension module",
    ext_modules=[module],
    script_args=["build_ext", "--inplace", "--build-lib", "."],
    options={
        "build_ext": {
            "build_lib": ".",
        },
    },
)
