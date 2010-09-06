'''
Tool dedicated for Thomas (with lot of love, by Mathieu ^^)
It wipe out all spaces and tabs at end of a line

Usage:
    python tools/cleanwhitespace.py
'''

import re
import os

endspacestab = re.compile('([\t\ ]*)$')

for root, dirs, files in os.walk('.'):
    files = [x for x in files if x[-3:] == '.py' and x[0] != '.']
    for file in files:
        filename = os.path.join(root, file)
        with open(filename, 'r') as fd:
            content = fd.read()
        lines = content.split('\r\n')
        changes = 0
        for idx in xrange(len(lines)):
            line = endspacestab.split(lines[idx], maxsplit=1)[0]
            if lines[idx] != line:
                changes += 1
                lines[idx] = line
        modified = '\r\n'.join(lines)
        if changes:
            print filename, ',', changes, 'removals'
            with open(filename, 'w') as fd:
                fd.write(modified)
