from distutils.core import setup
import py_iphelper.adapter_info

setup(
    name = 'py_iphelper',
    version = 0.0,
    description = 'Python wrapper for some Win32 IP Helper functions.',
    author = 'Joss Gray',
    author_email = 'joss@jossgray.net',
    url = 'https://github.com/jossgray/py_iphelper',
    packages = ['py_iphelper'],
    ext_modules = [py_iphelper.adapter_info.ffi.verifier.get_extension()]
)