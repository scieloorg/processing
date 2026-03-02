#!/usr/bin/env python3
"""
Creates and installs a 'thriftpy' compatibility shim that delegates to thriftpy2.
Needed because articlemetaapi and other packages import 'thriftpy' directly,
but thriftpy==0.3.9 cannot compile on Python 3.12+.
thriftpy2 is the maintained Python 3 fork of thriftpy with identical API.
"""
import os
import sys
import subprocess
import tempfile
import shutil

td = tempfile.mkdtemp()
try:
    pkg = os.path.join(td, 'thriftpy')
    submodules = ['', 'rpc', 'transport', 'protocol', 'contrib']

    for sub in submodules:
        path = os.path.join(pkg, sub) if sub else pkg
        os.makedirs(path, exist_ok=True)
        src = f'thriftpy2.{sub}' if sub else 'thriftpy2'
        with open(os.path.join(path, '__init__.py'), 'w') as f:
            f.write(f'from {src} import *\n')

    with open(os.path.join(td, 'setup.py'), 'w') as f:
        f.write('from setuptools import setup, find_packages\n')
        f.write("setup(name='thriftpy', version='99.0.0', packages=find_packages())\n")

    subprocess.run(
        [sys.executable, '-m', 'pip', 'install', '--no-cache-dir', td],
        check=True
    )
    print("thriftpy compatibility shim installed successfully")
finally:
    shutil.rmtree(td, ignore_errors=True)
