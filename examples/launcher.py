#!/usr/bin/env python

import subprocess
proc = subprocess.Popen(['python', 'start.py'], cwd='desktop')
proc.wait()
