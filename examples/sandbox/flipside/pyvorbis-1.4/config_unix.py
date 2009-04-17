#!/usr/bin/env python

import string
import os
import sys
import exceptions

log_name = 'config.log'
if os.path.isfile(log_name):
    os.unlink(log_name)

def write_log(msg):
    log_file = open(log_name, 'a')
    log_file.write(msg)
    log_file.write('\n')
    log_file.close()

def exit(code=0):
    sys.exit(code)

def msg_checking(msg):
    print "Checking", msg, "...",

def execute(cmd):
    write_log("Execute: %s" % cmd)
    full_cmd = '%s 1>>%s 2>&1' % (cmd, log_name)
    return os.system(full_cmd)

def run_test(input, flags = ''):
    try:
        f = open('_temp.c', 'w')
        f.write(input)
        f.close()
        compile_cmd = '%s -o _temp _temp.c %s' % (os.environ.get('CC', 'cc'),
                                                  flags)
        write_log("executing test: %s" % compile_cmd)
        if not execute(compile_cmd):
            execute('./_temp')
                
    finally:
        execute('rm -f _temp.c _temp')
    
ogg_test_program = '''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ogg/ogg.h>

int main ()
{
  system("touch conf.oggtest");
  return 0;
}
'''

def find_ogg(ogg_prefix = '/usr/local', enable_oggtest = 1):
    """A rough translation of ogg.m4"""

    ogg_include_dir = ogg_prefix + '/include'
    ogg_lib_dir = ogg_prefix + '/lib'
    ogg_libs = 'ogg'

    msg_checking('for Ogg')

    if enable_oggtest:
        execute('rm -f conf.oggtest')

        try:
            run_test(ogg_test_program, flags="-I" + ogg_include_dir)
            if not os.path.isfile('conf.oggtest'):
                raise RuntimeError, "Did not produce output"
            execute('rm conf.oggtest')
            
        except:
            print "test program failed"
            return None

    print "success"

    return {'ogg_libs' : ogg_libs,
            'ogg_lib_dir' : ogg_lib_dir,
            'ogg_include_dir' : ogg_include_dir}


vorbis_test_program = '''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <vorbis/codec.h>

int main ()
{
  system("touch conf.vorbistest");
  return 0;
}
'''

def find_vorbis(ogg_data,
                vorbis_prefix = '/usr/local',
                enable_vorbistest = 1):
    """A rough translation of vorbis.m4"""

    ogg_libs = ogg_data['ogg_libs']
    ogg_lib_dir = ogg_data['ogg_lib_dir']
    ogg_include_dir = ogg_data['ogg_include_dir']
    
    vorbis_include_dir = vorbis_prefix + '/include'
    vorbis_lib_dir = vorbis_prefix + '/lib'
    vorbis_libs = 'vorbis vorbisfile vorbisenc'

    msg_checking('for Vorbis')

    if enable_vorbistest:
        execute('rm -f conf.vorbistest')

        try:
            run_test(vorbis_test_program,
                     flags = "-I%s -I%s" % (vorbis_include_dir,
                                            ogg_include_dir))
            if not os.path.isfile('conf.vorbistest'):
                raise RuntimeError, "Did not produce output"
            execute('rm conf.vorbistest')
            
        except:
            print "test program failed"
            return None

    print "success"

    return {'vorbis_libs' : vorbis_libs,
            'vorbis_lib_dir' : vorbis_lib_dir,
            'vorbis_include_dir' : vorbis_include_dir}

def write_data(data):
    f = open('Setup', 'w')
    for item in data.items():
        f.write('%s = %s\n' % item)
    f.close()
    print "Wrote Setup file"
            
def print_help():
    print '''%s
    --prefix                  Give the prefix in which vorbis was installed.
    --with-ogg-dir [dir]      Give the directory for ogg files
                                (separated by a space)
    --with-vorbis-dir [dir]   Give the directory for vorbis files''' % sys.argv[0]
    exit()

def parse_args():
    def arg_check(data, argv, pos, arg_type, key):
        "Register an command line arg which takes an argument"
        if len(argv) == pos:
            print arg_type, "needs an argument"
            exit(1)
        data[key] = argv[pos]
        
    data = {}
    argv = sys.argv
    for pos in range(len(argv)):
        if argv[pos] == '--help':
            print_help()
        if argv[pos] == '--with-ogg-dir':
            pos = pos + 1
            arg_check(data, argv, pos, "Ogg dir", 'ogg_prefix')
        if argv[pos] == '--with-vorbis-dir':
            pos = pos + 1
            arg_check(data, argv, pos, "Vorbis dir", 'vorbis_prefix')
        if argv[pos] == '--prefix':
            pos = pos + 1
            arg_check(data, argv, pos, "Prefix", 'prefix')

    return data
    
def main():
    args = parse_args()
    prefix = args.get('prefix', '/usr/local')
    vorbis_prefix = args.get('vorbis_prefix', prefix)
    ogg_prefix = args.get('ogg_prefix', prefix)

    data = find_ogg(ogg_prefix = ogg_prefix)
    if not data:
        print "Config failure"
        exit(1)

    vorbis_data = find_vorbis(ogg_data = data,
                              vorbis_prefix = vorbis_prefix)
    if not vorbis_data:
        print "Config failure"
        exit(1)
    data.update(vorbis_data)
    
    write_data(data)

if __name__ == '__main__':
    main()




