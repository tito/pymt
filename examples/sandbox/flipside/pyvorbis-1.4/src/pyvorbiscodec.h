#ifndef __VORBISCODEC_H__
#define __VORBISCODEC_H__

#include <Python.h>
#include <vorbis/codec.h>

typedef struct {
  PyObject_HEAD
  vorbis_dsp_state vd;
  PyObject *parent;
} py_dsp;

typedef struct {
  PyObject_HEAD
  vorbis_block vb;
  PyObject *parent;
} py_block;

#define PY_DSP(x) (&(((py_dsp *) (x))->vd))
#define PY_BLOCK(x) (&(((py_block *) (x))->vb))

extern PyTypeObject py_dsp_type;
extern PyTypeObject py_block_type;

PyObject *py_dsp_from_dsp(vorbis_dsp_state *vd, PyObject *parent);
PyObject *py_block_from_block(vorbis_block *vb, PyObject *parent);

#endif /* __VORBISCODEC_H__ */
















