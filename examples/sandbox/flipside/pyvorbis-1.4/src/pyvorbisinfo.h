#ifndef __PYVORBIS_INFO_H__
#define __PYVORBIS_INFO_H__

#include <vorbis/vorbisfile.h>

typedef struct {
  PyObject_HEAD
  vorbis_info vi;
} py_vinfo;

typedef struct {
  PyObject_HEAD
	int malloced;
  vorbis_comment *vc;
  PyObject *parent;
} py_vcomment;

#define PY_VINFO(x) (&(((py_vinfo *) (x))->vi))
#define PY_VCOMMENT(x) ((((py_vcomment *) (x))->vc))

extern PyTypeObject py_vinfo_type;
extern PyTypeObject py_vcomment_type;

PyObject *py_info_new_from_vi(vorbis_info *vi);
PyObject *py_info_new(PyObject *, PyObject *, PyObject *);

PyObject *py_comment_new_from_vc(vorbis_comment *vc, PyObject *parent);
PyObject *py_comment_new(PyObject *, PyObject *);

#endif /* __PYVORBIS_INFO_H__ */

