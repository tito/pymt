#!/usr/bin/env python

import subprocess
proc = subprocess.Popen(['python', 'menu.py'], cwd='applauncher')
proc.wait()
