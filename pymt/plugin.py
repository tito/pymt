import sys
import os

class MTPlugins(object):
    def __init__(self, plugin_paths=['../examples/']):
        self.plugin_paths = plugin_paths
        self.plugins = {}
        self.plugins_loaded = False

    def update_sys_path(self):
        for path in self.plugin_paths:
            if path not in sys.path:
                sys.path.append(path)

    def search_plugins(self):
        self.update_sys_path()
        for path in self.plugin_paths:
            try:
                l = os.listdir(path)
            except:
                continue
            for plugin in l:
                try:
                    a = __import__(name='%s.%s' % (plugin, plugin), fromlist=plugin)
                    if not a.IS_PYMT_PLUGIN:
                        continue
                    self.plugins[plugin] = a
                except Exception, e:
                    pass

    def list(self):
        if not self.plugins_loaded:
            self.search_plugins()
        return self.plugins

    def get_plugin(self, name):
        return self.plugins[name]

    def get_key(self, plugin, key, default_value=''):
        try:
            return plugin.__getattribute__(key)
        except:
            return default_value

    def get_infos(self, plugin):
        return {
            'title': self.get_key(plugin, 'PLUGIN_TITLE'),
            'author': self.get_key(plugin, 'PLUGIN_AUTHOR'),
            'email': self.get_key(plugin, 'PLUGIN_EMAIL'),
            'description': self.get_key(plugin, 'PLUGIN_DESCRIPTION'),
            'icon': self.get_key(plugin, 'PLUGIN_ICON')
        }

    def activate(self, plugin, container):
        plugin.pymt_plugin_activate(container)

    def deactivate(self, plugin, container):
        plugin.pymt_plugin_deactivate(container)


if __name__ == '__main__':
    a = MTPlugins()
    for plugin in a.list():
        print a.get_infos(a.get_plugin(plugin))
