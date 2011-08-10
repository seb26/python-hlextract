# Copyright (c) 2011 seb26. All rights reserved.
# Source code is licensed under the terms of the Modified BSD License.

import os
import re
import ctypes
from subprocess import Popen, PIPE, STDOUT
from collections import defaultdict

class HLExtract:

    def __init__(self):
        self.dll = ctypes.WinDLL(r'.\bin\HLLib.dll')
        print 'hello world'