import os, sys
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
'''===================================================================
$SUMMARY
===================================================================

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


# Generation finished
print 'Generation finished, do make html'
