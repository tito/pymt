from subprocess import *
import os

system_lib = ['re', 'optparse', 'os', 'sys', 'shutil', 'warnings', 'Queue', 'osc', 'numpy', 'math', 'xml.dom', 'logging', 'random', 'ctypeasc', 'ConfigParser', 'getopt', 'ctypes', 'gzip', 'urllib', 'gtk', 'operator', 'time']
system_lib_find = ['cssutils', 'pyglet', 'encutils', 'squirtle', 'factory']

def f9(seq):
    # Not order preserving
    return {}.fromkeys(seq).keys()

cmd = "find pymt -iname '*.py' -exec grep -H 'import' {} \;"
output = Popen(cmd, shell=True, stdout=PIPE).communicate()[0]
cmps = []

for line in output.split("\n"):
	if line == '':
		continue
	if line.find('`') > 0:
		continue
	if line.find('=') > 0:
		continue
	filename, line = map(lambda x: x.strip(), line.split(':', 1))
	line = line.rsplit('#', 1)[0]
	filename = filename[:-3]
	if line.startswith('import'):
		line = line[7:].replace(' ', '').split(',')
		for k in line:
			cmps.append((filename, k))
	elif line.startswith('from'):
		line = line[4:].rsplit('import', 1)[0].strip()
		cmps.append((filename, line))

# remove init
cmps2 = []
for a, b in cmps:
	p = 0
	for s in system_lib:
		if s in b:
			p = 1
		if s in a:
			p = 1
	for s in system_lib_find:
		if b.find(s) >= 0:
			p = 1
		if a.find(s) >= 0:
			p = 1
	if p:
		continue
	if os.path.basename(a) == '__init__':
		a = a[:-9]
	cmps2.append((a, b))
cmps = cmps2

# resolve path in b
cmps2 = []
kcmp = f9(map(lambda x: x[0], cmps))
for a, b in cmps:
	nb = b.lstrip('.')
	nbp = len(b) - len(nb)
	bc = b = b.replace('.', '/')
	if nbp > 0:
		bc = ('../' * nbp) + b

	# test in current directory
	c = os.path.normpath(os.path.join(a, bc))
	if os.path.exists(c + '.py'):
		b = c
	elif os.path.exists(c):
		b = c
	elif os.path.exists(os.path.normpath(os.path.join(a, '../', bc))):
		b = os.path.normpath(os.path.join(a, '../', bc))
	elif os.path.exists(os.path.normpath(os.path.join(a, '../', bc)) + '.py'):
		b = os.path.normpath(os.path.join(a, '../', bc))
	else:
		pass

	# append
	cmps2.append((a, b))
cmps = cmps2

print 'digraph {'
for a, b in cmps:
	print '"%s" -> "%s"' % (b, a)
print '}'
