#!/usr/bin/env python

import subprocess, sys
proc = subprocess.Popen(['python', 'start.py'] + sys.argv[1:], cwd='desktop')
proc.wait()
