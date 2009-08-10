import os
import sys
import re
import pymt


# Directory of doc
base_dir = os.path.dirname(__file__)
dest_dir = os.path.join(base_dir, 'sources')

def writefile(filename, data):
	global dest_dir
	print 'write', filename
	f = os.path.join(dest_dir, filename)
	h = open(f, 'w')
	h.write(data)
	h.close()


# Search all pymt module
l = [(x, sys.modules[x], os.path.basename(sys.modules[x].__file__).rsplit('.', 1)[0]) for x in sys.modules if x.startswith('pymt') and sys.modules[x]]

# Extract packages from modules
packages = []
modules = {}
for name, module, filename in l:
	if filename == '__init__':
		packages.append(name)
	else:
		if hasattr(module, '__all__'):
			modules[name] = module.__all__
		else:
			modules[name] = [x for x in dir(module) if not x.startswith('__')]

packages.sort()

# Create index
api_index = \
'''===================================================================
API documentation for PyMT
===================================================================

.. toctree::

'''
for package in packages:
	api_index += "    api-%s.rst\n" % package

writefile('api-index.rst', api_index)

# Create index for all packages
template = \
'''==========================================================================================================
$SUMMARY
==========================================================================================================

.. automodule:: $PACKAGE
    :members:
    :show-inheritance:

.. toctree::

'''
for package in packages:
	try:
		summary = [x for x in sys.modules[package].__doc__.split("\n") if len(x) > 1][0]
		try:
			title, content = summary.split(':', 1)
			summary = '**%s**: %s' % (title, content)
		except:
			pass
	except:
		summary = 'NO DOCUMENTATION (package %s)' % package
	t = template.replace('$SUMMARY', summary).replace('$PACKAGE', package)

	# search modules
	m = modules.keys()
	m.sort()
	for module in m:
		packagemodule = module.rsplit('.', 1)[0]
		if packagemodule != package:
			continue
		t += "    api-%s.rst\n" % module

	writefile('api-%s.rst' % package, t)


# Create index for all module
m = modules.keys()
m.sort()
for module in m:
	try:
		summary = [x for x in sys.modules[module].__doc__.split("\n") if len(x) > 1][0]
		try:
			title, content = summary.split(':', 1)
			summary = '**%s**: %s' % (title, content)
		except:
			pass
	except:
		summary = 'NO DOCUMENTATION (module %s)' % module
	t = template.replace('$SUMMARY', summary).replace('$PACKAGE', module)
	writefile('api-%s.rst' % module, t)


# Extract doc from available tutorials
tuts_base_dir = os.path.join(os.path.dirname(__file__), '..', 'examples', 'tutorials')
tuts_files = []
for tutid in os.listdir(tuts_base_dir):
	tutdir = os.path.join(tuts_base_dir, tutid)
	if not os.path.isdir(tutdir):
		continue

	# Got a tutorial
	for filename in os.listdir(tutdir):
		if filename[-3:] != '.py':
			continue
		tutfilename = filename[:-3]
		tuts_files.append((tutid, tutfilename))

		# Extract header
		data = file(os.path.join(tutdir, filename), 'r').read()
		result = re.search("^('''|\"\"\")(.*)('''|\"\"\")", data, re.S)
		doc = ''
		if result is None:
			doc = 'No documentation available for %s : %s' % (tutid, filename)
		else:
			doc = result.groups()[1].strip("\n")

		writefile('tutorial-%s-%s.rst' % (tutid, tutfilename), doc)

# Write it :)
tut_index = \
'''===================================================================
API documentation for PyMT
===================================================================

.. toctree::

'''
for tutid, tutfilename in tuts_files:
	tut_index += "    tutorial-%s-%s.rst\n" % (tutid, tutfilename)

writefile('tutorial-index.rst', tut_index)


# Generation finished
print 'Generation finished, do make html'
