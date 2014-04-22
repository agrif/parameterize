#!/usr/bin/env python

# since this may be run under py2
from __future__ import print_function

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup
from subprocess import Popen, PIPE
import sys
import os

def find_version():
    try:
        p = Popen('git describe --tags --match "v*.*"', stdout=PIPE, stderr=PIPE, shell=True)
        p.stderr.close()
        line = p.stdout.readlines()[0]
        line = line.decode().strip()
        if line.startswith('v'):
            line = line[1:]
            return line
    except Exception as e:
        pass
    
    # if we get here, git tags failed
    # attempt to read PKG-INFO
    try:
        with open("PKG-INFO") as f:
            for line in f.readlines():
                line = line.strip().split(": ")
                if line[0] == "Version":
                    return line[1]
    except Exception:
        pass
    
    # if we get HERE, nothing worked
    print("warning: git version or PKG-INFO file not found. version will be wrong!", file=sys.stderr)
    return "0.0-unknown"

if __name__ == '__main__':
    # force this to run in the right directory
    os.chdir(os.path.abspath(os.path.split(__file__)[0]))
    
    setup(name='parameterize',
          version=find_version(),
          description='a Python implementation of parameterize and SRFI 39',
          author='Aaron Griffith',
          author_email='aargri@gmail.com',
          url='http://github.com/agrif/parameterize',
          license='MIT',
          keywords = ['parameters', 'parameterize', 'dynamic scope'],
          classifiers = [
              'Development Status :: 3 - Alpha',
              'License :: OSI Approved :: MIT License',
              'Programming Language :: Python :: 2.7',
              'Programming Language :: Python :: 3',
          ],
          py_modules=['parameterize'],
          test_suite='tests',
          setup_requires = ['setuptools_git >= 0.3'],
    )
