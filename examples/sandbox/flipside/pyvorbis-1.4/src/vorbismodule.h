#ifndef __VORBISMODULE_H__
#define __VORBISMODULE_H__

#include <Python.h>
#include <pyogg/pyogg.h>

#include "general.h"

ogg_module_info *modinfo;

PyObject *Py_VorbisError;

/* Object docstrings */

extern char py_vorbisfile_doc[];
extern char py_vinfo_doc[];
extern char py_vcomment_doc[];
extern char py_dsp_doc[];

/* Utility functions/macros */

PyObject *v_error_from_code(int, char*);

#define RETURN_IF_VAL(val, msg)    if (val < 0) { \
                                       return v_error_from_code(val, msg); \
                                   } \
                                   Py_INCREF(Py_None); \
                                   return Py_None;


#endif /* __VORBISMODULE_H__ */

