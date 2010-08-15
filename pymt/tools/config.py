#!/usr/bin/env python

from __future__ import with_statement
from Tkinter import *
import tkMessageBox
import sys
import os
os.environ['PYMT_SHADOW_WINDOW'] = '0'
from pymt import pymt_modules, pymt_config, pymt_config_fn, curry, TouchFactory

class AutoConfig(dict):
    def __getitem__(self, name):
        if not self.__contains__(name):
            section, id = name.split('.', 1)
            value = pymt_config.get(section, id)
            var = StringVar()
            var.set(value)
            self.__setitem__(name, var)
        return super(AutoConfig, self).__getitem__(name)

master = Tk()
master.title('PyMT Configuration')
c = AutoConfig()
c_tuio_host = StringVar()
c_tuio_port = StringVar()
c_modules = StringVar()
c_screen = StringVar()
c_input = StringVar()
c_input_option = StringVar()
c_input_provider = StringVar()
c_input_devicename = StringVar()

try:
    provider = pymt_config.get('input', 'default')
    name, args = provider.split(',', 1)
    host, port = args.split(':', 1)
    c_tuio_host.set(host)
    c_tuio_port.set(port)
except:
    c_tuio_host.set('0.0.0.0')
    c_tuio_port.set('3333')

c_screen.set('%dx%d' % (pymt_config.getint('graphics', 'width'),
                        pymt_config.getint('graphics', 'height')))

# Get infos
opt_input = TouchFactory.list()
opt_fbo = ('hardware', 'software')
opt_loglevel = ('debug', 'info', 'warning', 'error')
opt_screen = (
    '320x240',
    '640x480',
    '800x600',
    '1024x768',
    '1280x720',
    '1280x1024',
    '1280x1080',
    '1400x1050',
    '1440x900',
    '1440x1080',
    '1600x1200',
    '1680x1050',
    '1920x1080',
    '1920x1200',
    '2560x1600',
)

# ================================================================
# Config functions
# ================================================================

def configuration_debug():
    for key in c:
        print key, '=', c.get(key).get()

def configuration_save():
    for key in c:
        section, name = key.split('.', 1)
        value = c.get(key).get()
        if name in ('double_tap_time', 'double_tap_distance'):
            value = int(float(value))
        pymt_config.set(section, name, value)

    # modules
    if pymt_config.has_section('modules'):
        pymt_config.remove_section('modules')
    pymt_config.add_section('modules')
    modlist = eval(c_modules.get())
    for index in map(int, e_modules_list.curselection()):
        pymt_config.set('modules', modlist[index], '')

    # screen
    width, height = c_screen.get().split('x')
    pymt_config.set('graphics', 'width', width)
    pymt_config.set('graphics', 'height', height)

    # input
    if pymt_config.has_section('input'):
        pymt_config.remove_section('input')
    pymt_config.add_section('input')
    inputlist = eval(c_input.get())
    for index in map(int, e_input_list.curselection()):
        device_id, option = inputlist[index].split('=', 1)
        pymt_config.set('input', device_id, option)

    try:
        pymt_config.write()
        tkMessageBox.showinfo('PyMT', 'Configuration saved !')
    except Exception, e:
        tkMessageBox.showwarning('PyMT', 'Unable to save default configuration : ' + str(e))


# ================================================================
# PyMT
# ================================================================

g_pymt = LabelFrame(master, text='General', padx=5, pady=5)
g_pymt.grid(row=0, column=0, sticky=W+E+N+S)

Label(g_pymt, text='Show FPS').grid(row=0)
Label(g_pymt, text='Show event stats').grid(row=1)
Label(g_pymt, text='Log level').grid(row=2)
Label(g_pymt, text='Double tap time').grid(row=3)
Label(g_pymt, text='Double tap distance').grid(row=4)
Label(g_pymt, text='Retain Time').grid(row=5)
Label(g_pymt, text='Retain Distance').grid(row=6)

e_pymt_fps = Checkbutton(g_pymt,
        variable=c['pymt.show_fps'], onvalue='1', offvalue='0')
e_pymt_eventstats = Checkbutton(g_pymt,
        variable=c['pymt.show_eventstats'], onvalue='1', offvalue='0')
e_pymt_loglevel = OptionMenu(g_pymt, c['pymt.log_level'], *opt_loglevel)
e_pymt_doubletaptime = Scale(g_pymt, from_=0, to=1000, orient=HORIZONTAL,
        variable=c['pymt.double_tap_time'])
e_pymt_doubletapdistance = Scale(g_pymt, from_=0, to=300, orient=HORIZONTAL,
        variable=c['pymt.double_tap_distance'])
e_pymt_retaintime = Entry(g_pymt, textvariable=c['pymt.retain_time'])
e_pymt_retaindistance = Entry(g_pymt, textvariable=c['pymt.retain_distance'])

e_pymt_fps.grid(row=0, column=1)
e_pymt_eventstats.grid(row=1, column=1)
e_pymt_loglevel.grid(row=2, column=1)
e_pymt_doubletaptime.grid(row=3, column=1, sticky=W+E+N+S)
e_pymt_doubletapdistance.grid(row=4, column=1, sticky=W+E+N+S)
e_pymt_retaintime.grid(row=5,column=1)
e_pymt_retaindistance.grid(row=6,column=1)

# ================================================================
# Graphics
# ================================================================

g_graphics = LabelFrame(master, text='Graphics', padx=5, pady=5)
g_graphics.grid(row=0, column=1, sticky=W+E+N+S)

Label(g_graphics, text='Fullscreen').grid(row=0)
Label(g_graphics, text='Screen').grid(row=1)
Label(g_graphics, text='Display').grid(row=2)
Label(g_graphics, text='Line smooth').grid(row=3)
Label(g_graphics, text='Vertical sync').grid(row=4)
Label(g_graphics, text='FBO').grid(row=5)
Label(g_graphics, text='Multisamples').grid(row=6)
Label(g_graphics, text='Show Cursor').grid(row=7)

e_graphics_fullscreen = Checkbutton(g_graphics,
        variable=c['graphics.fullscreen'], onvalue='1', offvalue='0')
e_graphics_screen = OptionMenu(g_graphics, c_screen, *opt_screen)
e_graphics_display = Spinbox(g_graphics, from_=-1, to=100, textvariable=c['graphics.display'])
e_graphics_line_smooth = Checkbutton(g_graphics,
        variable=c['graphics.line_smooth'], onvalue='1', offvalue='0')
e_graphics_vertical_sync = Checkbutton(g_graphics,
        variable=c['graphics.vsync'], onvalue='1', offvalue='0')
e_graphics_fbo = OptionMenu(g_graphics, c['graphics.fbo'], *opt_fbo)
e_graphics_multisamples = Entry(g_graphics, textvariable=c['graphics.multisamples'])
e_graphics_showcursor = Checkbutton(g_graphics,
        variable=c['graphics.show_cursor'], onvalue='1', offvalue='0')

e_graphics_fullscreen.grid(row=0, column=1)
e_graphics_screen.grid(row=1, column=1)
e_graphics_display.grid(row=2, column=1)
e_graphics_line_smooth.grid(row=3, column=1)
e_graphics_vertical_sync.grid(row=4, column=1)
e_graphics_fbo.grid(row=5, column=1)
e_graphics_multisamples.grid(row=6, column=1)
e_graphics_showcursor.grid(row=7, column=1)


# ================================================================
# Modules
# ================================================================

g_modules = LabelFrame(master, text='General', padx=5, pady=5)
g_modules.grid(row=1, column=1, sticky=W+E+N+S)

Label(g_modules, text='Modules').grid(row=0)

e_modules_list = Listbox(g_modules, selectmode=MULTIPLE,
    exportselection=0, listvariable=c_modules)

e_modules_list.grid(row=0, column=1)

# ================================================================
# Inputs
# ================================================================

g_input = LabelFrame(master, text='Input', padx=5, pady=5)
g_input.grid(row=1, column=0, sticky=W+E+N+S)

e_input_list = Listbox(g_input, selectmode=MULTIPLE,
    exportselection=0, listvariable=c_input)
e_input_list.grid(row=0, column=1)

Label(g_input, text='Device Name').grid(row=1)
Label(g_input, text='Provider').grid(row=2)
Label(g_input, text='Option').grid(row=3)

e_input_devicename = Entry(g_input, textvariable=c_input_devicename)
e_input_devicename.grid(row=1, column=1)

e_input_available = OptionMenu(g_input, c_input_provider, *opt_input)
e_input_available.grid(row=2, column=1)

e_input_option = Entry(g_input, textvariable=c_input_option)
e_input_option.grid(row=3, column=1)

def _input_add(*largs):
    device_id = c_input_devicename.get()
    if device_id == '':
        tkMessageBox.showerror('PyMT', 'No device name setted')
        return
    provider_name = c_input_provider.get()
    if provider_name == '':
        tkMessageBox.showerror('PyMT', 'No provider selected')
        return
    options = c_input_option.get()
    t = '%s=%s,%s' % (str(device_id), str(provider_name), str(options))
    e_input_list.insert(END, t)
    e_input_list.selection_set(eval(c_input.get()).index(t))

    c_input_devicename.set('')
    c_input_option.set('')

e_input_add = Button(g_input, text='Add input', command=_input_add)
e_input_add.grid(row=4, column=1)


# ================================================================
# Buttons
# ================================================================

btn_save = Button(master, text='Save configuration', command=configuration_save)
btn_save.grid(row=2, column=0, sticky=W+E+N+S)
btn_quit = Button(master, text='Exit', command=curry(sys.exit, 0))
btn_quit.grid(row=2, column=1, sticky=W+E+N+S)

# ================================================================
# Fill list
# ================================================================
for mod in pymt_modules.list():
    e_modules_list.insert(END, mod)
for opt in pymt_config.options('modules'):
    index = eval(c_modules.get()).index(opt)
    e_modules_list.selection_set(index)
for device_id in pymt_config.options('input'):
    line = pymt_config.get('input', device_id)
    t = '%s=%s' % (str(device_id), str(line))
    e_input_list.insert(END, t)
    e_input_list.selection_set(eval(c_input.get()).index(t))

# ================================================================
# Load configuration
# ================================================================

try:
    mainloop()
finally:
    pass
