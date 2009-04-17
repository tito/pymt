#ifndef __GENERAL_H__
#define __GENERAL_H__

#include <Python.h>
#include <ogg/ogg.h>

#define MSG_SIZE 256
#define KEY_SIZE 1024

#define PY_UNICODE (PY_VERSION_HEX >= 0x01060000)

ogg_int64_t arg_to_64(PyObject *longobj);

#define FDEF(x) static PyObject *py_##x (PyObject *self, PyObject *args); \
static char py_##x##_doc[] = 

#endif /* __GENERAL_H__ */









