#ifndef __PYVORBIS_FILE_H__
#define __PYVORBIS_FILE_H__

#include <Python.h>
#include <vorbis/vorbisfile.h>

typedef struct {
  PyObject_HEAD
  OggVorbis_File *ovf;
  PyObject *py_file;
  FILE *c_file;
} py_vorbisfile;

#define PY_VORBISFILE(x) (((py_vorbisfile *)x)->ovf)
#define PY_VORBISFILEOBJECT(x) (((py_vorbisfile *)x)->py_file)
extern PyTypeObject py_vorbisfile_type;

PyObject *py_file_new(PyObject *, PyObject *);

#endif /* __PYVORBIS_FILE_H__ */




