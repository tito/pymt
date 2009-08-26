'''
Modules: UI module you can plug on any running PyMT apps.
'''

__all__ = ['pymt_modules']

import pymt
import os
import sys

class ModuleContext:
    '''Generic class to add any attributes in.'''
    pass

class Modules:
    def __init__(self, **kwargs):
        self.mods = {}
        self.wins = []

    def add_path(self, path):
        '''Add a path to search modules in'''
        if not os.path.exists(path):
            return
        if path not in sys.path:
            sys.path.append(path)
        dirs = os.listdir(path)
        for module in dirs:
            if module[-3:] != '.py' or module == '__init__.py':
                continue
            module = module[:-3]
            self.mods[module] = {'id': module, 'activated': False, 'context': ModuleContext()}

    def list(self):
        '''Return the list of available modules'''
        return self.mods

    def import_module(self, key):
        module = __import__(name=key, fromlist='mods')
        # basic check on module
        if not hasattr(module, 'start'):
            pymt.pymt_logger.warning('Module <%s> missing start() function' %
                                     key)
            return
        if not hasattr(module, 'stop'):
            pymt.pymt_logger.warning('Module <%s> missing stop() function' % key)
            return
        self.mods[key]['module'] = module

    def activate_module(self, key, win):
        '''Activate a module on a window'''
        if not key in self.mods:
            pymt.pymt_logger.warning('Module <%s> not found' % key)
            return

        if not 'module' in self.mods[key]:
            self.import_module(key)

        module = self.mods[key]['module']
        if not self.mods[key]['activated']:
            module.start(win, self.mods[key]['context'])

    def deactivate_module(self, key, win):
        '''Deactivate a module from a window'''
        if not key in self.mods:
            pymt.pymt_logger.warning('Module <%s> not found' % key)
            return
        if not hasattr(self.mods[key], 'module'):
            return
        module = self.mods[key]['module']
        if self.mods[key]['activated']:
            module.stop(win, self.mods[key]['context'])

    def register_window(self, win):
        '''Add window in window list'''
        self.wins.append(win)
        self.update()

    def unregister_window(self, win):
        '''Remove window from window list'''
        self.wins.remove(win)
        self.update()

    def update(self):
        '''Update status of module for each windows'''
        modules_to_activate = map(lambda x: x[0], pymt.pymt_config.items('modules'))
        for win in self.wins:
            for key in self.mods:
                if not key in modules_to_activate:
                    self.deactivate_module(key, win)
            for key in modules_to_activate:
                self.activate_module(key, win)

    def usage_list(self):
        print
        print 'Available modules'
        print '================='
        for module in self.list():
            if not 'module' in self.mods[module]:
                self.import_module(module)
            text = self.mods[module]['module'].__doc__.strip("\n ")
            print '%-12s: %s' % (module, text)
        print

pymt_modules = Modules()
pymt_modules.add_path(pymt.pymt_modules_dir)
if not os.path.basename(sys.argv[0]).startswith('sphinx'):
    pymt_modules.add_path(pymt.pymt_usermodules_dir)

if __name__ == '__main__':
    print pymt_modules.list()
