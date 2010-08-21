#!/usr/bin/env python

import subprocess, sys, os
desktop_dir = os.path.join(os.path.dirname(__file__), 'desktop')
proc = subprocess.Popen([sys.executable, 'desktop-single.py'] + sys.argv[1:],
                        cwd=desktop_dir)
proc.wait()
