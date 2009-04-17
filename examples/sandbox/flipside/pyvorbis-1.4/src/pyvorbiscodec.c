#include <assert.h>
#include <vorbis/vorbisenc.h>

#include "general.h"
#include "vorbismodule.h"

#include "pyvorbiscodec.h"
#include "pyvorbisinfo.h"

#define MIN(x,y) ((x) < (y) ? (x) : (y))

/**************************************************************
                         VorbisDSP Object
**************************************************************/

FDEF(vorbis_analysis_headerout) "Create three header packets for an ogg\n"
"stream, given an optional comment object.";
FDEF(vorbis_analysis_blockout) "Output a VorbisBlock. Data must be written to the object first.";

FDEF(vorbis_block_init) "Create a VorbisBlock object for use in encoding {more?!}";
FDEF(dsp_write) "Write audio data to the dsp device and have it analyzed. \n"
"Each argument must be a string containing the audio data for a\n"
"single channel.\n"
"If None is passed as the only argument, this will signal that no more\n"
"data needs to be written.";
FDEF(dsp_write_wav) "Write audio data to the dsp device and have it analyzed.\n"
"The single argument is the output from the python wave module. Only supports\n"
"16-bit wave data (8-bit waves will produce garbage).";
FDEF(dsp_close) "Signal that all audio data has been written to the object.";
FDEF(vorbis_bitrate_flushpacket) "";

static void py_dsp_dealloc(PyObject *);
static PyObject *py_dsp_getattr(PyObject *, char*);

char py_dsp_doc[] = "";

PyTypeObject py_dsp_type = {
  PyObject_HEAD_INIT(NULL)
  0,
  "VorbisDSPState",
  sizeof(py_dsp),
  0,

  /* Standard Methods */
  /* destructor */ py_dsp_dealloc,
  /* printfunc */  0,
  /* getattrfunc */ py_dsp_getattr,
  /* setattrfunc */ 0,
  /* cmpfunc */ 0,
  /* reprfunc */ 0,

  /* Type Categories */
  0, /* as number */
  0, /* as sequence */
  0, /* as mapping */
  0, /* hash */
  0, /* binary */
  0, /* repr */
  0, /* getattro */
  0, /* setattro */
  0, /* as buffer */
  0, /* tp_flags */
  py_dsp_doc,
};

static PyMethodDef DSP_methods[] = {
  {"headerout", py_vorbis_analysis_headerout,
   METH_VARARGS, py_vorbis_analysis_headerout_doc},
  {"blockout", py_vorbis_analysis_blockout,
   METH_VARARGS, py_vorbis_analysis_blockout_doc},
  {"create_block", py_vorbis_block_init,
   METH_VARARGS, py_vorbis_block_init_doc},
  {"write", py_dsp_write,
   METH_VARARGS, py_dsp_write_doc},
  {"write_wav", py_dsp_write_wav,
   METH_VARARGS, py_dsp_write_wav_doc},
  {"close", py_dsp_close,
   METH_VARARGS, py_dsp_close_doc},
  {"bitrate_flushpacket", py_vorbis_bitrate_flushpacket,
   METH_VARARGS, py_vorbis_bitrate_flushpacket_doc},
  {NULL, NULL}
};

PyObject *
py_dsp_from_dsp(vorbis_dsp_state *vd, PyObject *parent)
{
  py_dsp *ret = (py_dsp *) PyObject_NEW(py_dsp, &py_dsp_type);

  if (ret == NULL) 
    return NULL;
  
  ret->vd = *vd;
  ret->parent = parent;
  Py_XINCREF(parent);
  return (PyObject *) ret;
}

PyObject *
py_dsp_new(PyObject *self, PyObject *args)
{
  py_vinfo* py_vi;
  py_dsp *ret;
  vorbis_info *vi;
  vorbis_dsp_state vd;
  
  if (!PyArg_ParseTuple(args, "O!", &py_vinfo_type, &py_vi))
    return NULL;
  
  ret = (py_dsp *) PyObject_NEW(py_dsp, &py_dsp_type);
  ret->parent = NULL;
  vi = &py_vi->vi;
  vorbis_synthesis_init(&vd, vi);
  return py_dsp_from_dsp(&vd, (PyObject *) py_vi);
}

static void
py_dsp_dealloc(PyObject *self)
{
  vorbis_dsp_clear(PY_DSP(self));
  Py_XDECREF(((py_dsp *)self)->parent);
  PyMem_DEL(self);
}

static PyObject*
py_dsp_getattr(PyObject *self, char *name)
{
  return Py_FindMethod(DSP_methods, self, name);
}

static PyObject *
py_vorbis_analysis_blockout(PyObject *self, PyObject *args)
{
  vorbis_block vb;
  int ret;
  py_dsp *dsp_self = (py_dsp *) self;

  if (!PyArg_ParseTuple(args, ""))
    return NULL;

  vorbis_block_init(&dsp_self->vd, &vb);
  ret = vorbis_analysis_blockout(&dsp_self->vd, &vb);
  if (ret == 1)
    return py_block_from_block(&vb, self);
  else {
    Py_INCREF(Py_None);
    return Py_None;
  }
}

static PyObject *
py_vorbis_analysis_headerout(PyObject *self, PyObject *args)
{
  int code;
  py_dsp *dsp_self = (py_dsp *) self;
  py_vcomment *comm = NULL;
  vorbis_comment vc;
  ogg_packet header, header_comm, header_code;

  PyObject *pyheader = NULL;
  PyObject *pyheader_comm = NULL;
  PyObject *pyheader_code = NULL;
  PyObject *ret = NULL;
  
  /* Takes a comment object as the argument.
     I'll just give them an empty one if they don't provied one. */
  if (!PyArg_ParseTuple(args, "|O!", &py_vcomment_type, &comm))
    return NULL;
  
  if (comm == NULL) {
    vorbis_comment_init(&vc); /* Initialize an empty comment struct */
  } else {
    vc = *comm->vc;
  }
    
  if ((code = vorbis_analysis_headerout(&dsp_self->vd, &vc, &header,
					&header_comm, &header_code))) {
    v_error_from_code(code, "vorbis_analysis_header_out");
    goto finish;
  }
  
  /* Returns a tuple of oggpackets (header, header_comm, header_code) */
  
  pyheader = modinfo->ogg_packet_from_packet(&header);
  pyheader_comm = modinfo->ogg_packet_from_packet(&header_comm);
  pyheader_code = modinfo->ogg_packet_from_packet(&header_code);
  if (pyheader == NULL || pyheader_comm == NULL || pyheader_code == NULL)
    goto error;
  
  ret = PyTuple_New(3);
  PyTuple_SET_ITEM(ret, 0, pyheader);
  PyTuple_SET_ITEM(ret, 1, pyheader_comm);
  PyTuple_SET_ITEM(ret, 2, pyheader_code);
  
 finish:
  if (comm == NULL) /* Get rid of it if we created it */
    vorbis_comment_clear(&vc);
  return ret;
 error:
  if (comm == NULL)
    vorbis_comment_clear(&vc);
  Py_XDECREF(pyheader);
  Py_XDECREF(pyheader_comm);
  Py_XDECREF(pyheader_code);
  return NULL;
}

static PyObject *
py_vorbis_block_init(PyObject *self, PyObject *args)
{
  vorbis_block vb;
  py_dsp *dsp_self = (py_dsp *) self;
  PyObject *ret;

  if (!PyArg_ParseTuple(args, ""))
    return NULL;

  vorbis_block_init(&dsp_self->vd,&vb);
  ret = py_block_from_block(&vb, self);
  return ret;
}

/* Returns "len" if all arguments are strings of the same length, 
   -1 if one or more are not strings
   -2 if they have different lengths */

#define NON_STRING -1
#define DIFF_LENGTHS -2

static int
string_size(PyObject *args, int size)
{
  PyObject *cur;
  int k;
  int len = -1;

  for (k = 0; k < size; k++) {
    cur = PyTuple_GET_ITEM(args, k);
    if (!PyString_Check(cur))
      return NON_STRING;

    /* make sure the lengths are uniform */
    if (len == -1)
      len = PyString_Size(cur);
    else
      if (PyString_Size(cur) != len)
	return DIFF_LENGTHS;
  }
  return len;
}

static PyObject *
py_dsp_write(PyObject *self, PyObject *args)
{
  int k, channels;
  char err_msg[256];
  float **buffs;
  float **analysis_buffer;
  int len, samples;

  py_dsp *dsp_self = (py_dsp *) self;
  PyObject *cur;
  
  assert(PyTuple_Check(args));

  channels = dsp_self->vd.vi->channels;

  if (PyTuple_Size(args) == 1 && PyTuple_GET_ITEM(args, 0) == Py_None) {
    vorbis_analysis_wrote(&dsp_self->vd, 0);
    Py_INCREF(Py_None);
    return Py_None;
  }
  if (PyTuple_Size(args) != channels) {
    snprintf(err_msg, sizeof(err_msg), 
	     "Expected %d strings as arguments; found %d arguments",
	     channels, PyTuple_Size(args));
    PyErr_SetString(Py_VorbisError, err_msg);
    return NULL;
  }

  len = string_size(args, channels);
  if (len == NON_STRING) {
    PyErr_SetString(Py_VorbisError, 
		    "All arguments must be strings");
    return NULL;
  }
  if (len == DIFF_LENGTHS) {
    PyErr_SetString(Py_VorbisError, 
		    "All arguments must have the same length.");
    return NULL;
  }

  samples = len / sizeof(float);
  
  buffs = (float **) malloc(channels * sizeof(float *));
  for (k = 0; k < channels; k++) {
    cur = PyTuple_GET_ITEM(args, k);
    buffs[k] = (float *) PyString_AsString(cur);
  }

  analysis_buffer = vorbis_analysis_buffer(&dsp_self->vd, len * sizeof(float));
  for (k = 0; k < channels; k++)
    memcpy(analysis_buffer[k], buffs[k], len);

  free(buffs);
  vorbis_analysis_wrote(&dsp_self->vd, samples);

  return PyInt_FromLong(samples); /* return the number of samples written */
}

static void
parse_wav_data(const char *byte_data, float **buff, 
	       int channels, int samples)
{
  const float adjust = 1/32768.0;
  int j, k;
  for (j = 0; j < samples; j++) {
    for (k = 0; k < channels; k++) {
      float val = ((byte_data[j * 2 * channels + 2 * k + 1] << 8) | 
		   (byte_data[j * 2 * channels + 2 * k] & 0xff)) * adjust;
      buff[k][j] = val;
    }
  }
}

static PyObject *
py_dsp_write_wav(PyObject *self, PyObject *args) 
{
  const char *byte_data;
  int num_bytes, channels, k;
  long samples;
  const int samples_per_it = 1024;
  py_dsp *dsp = (py_dsp *) self;
  float **analysis_buffer;
  int sample_width;

  channels = dsp->vd.vi->channels;
  sample_width = channels * 2;

  if (!PyArg_ParseTuple(args, "s#", &byte_data, &num_bytes))
    return NULL;

  if (num_bytes % sample_width != 0) {
    PyErr_SetString(Py_VorbisError,
		    "Data is not a multiple of (2 * # of channels)");
    return NULL;
  }
  samples = num_bytes / sample_width;
	
  for (k = 0; 
       k < (samples + samples_per_it - 1) / samples_per_it; k++) {
    int to_write = MIN(samples - k * samples_per_it, samples_per_it);

    analysis_buffer = vorbis_analysis_buffer(&dsp->vd, 
					     to_write * sizeof(float));
    /* Parse the wav data directly into the analysis buffer. */
    parse_wav_data(byte_data, analysis_buffer, channels, to_write);

    /* Skip any data we've already passed by incrementing the pointer */
    byte_data += to_write * sample_width;

    vorbis_analysis_wrote(&dsp->vd, to_write);
  }
	
  return PyInt_FromLong(samples);
}

static PyObject *
py_dsp_close(PyObject *self, PyObject *args)
{
  py_dsp *dsp_self = (py_dsp *) self;
  vorbis_analysis_wrote(&dsp_self->vd, 0);
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
py_vorbis_bitrate_flushpacket(PyObject *self, PyObject *args)
{
  ogg_packet op;
  int ret;
	
  if (!PyArg_ParseTuple(args, ""))
    return NULL;

  ret = vorbis_bitrate_flushpacket(PY_DSP(self), &op);
  if (ret == 1) 
    return modinfo->ogg_packet_from_packet(&op);
  else if (ret == 0) {
    Py_INCREF(Py_None);
    return Py_None;
  } else {
    PyErr_SetString(Py_VorbisError, "Unknown return code from flushpacket");
    return NULL;
  }
}

/*********************************************************
			VorbisBlock
*********************************************************/
static void py_block_dealloc(PyObject *);
static PyObject *py_block_getattr(PyObject *, char*);

FDEF(vorbis_analysis) "Output an OggPage.";
FDEF(vorbis_bitrate_addblock) "?";

char py_block_doc[] = "";

PyTypeObject py_block_type = {
  PyObject_HEAD_INIT(NULL)
  0,
  "VorbisBlock",
  sizeof(py_block),
  0,

  /* Standard Methods */
  /* destructor */ py_block_dealloc,
  /* printfunc */ 0,
  /* getattrfunc */ py_block_getattr,
  /* setattrfunc */ 0,
  /* cmpfunc */ 0,
  /* reprfunc */ 0,

  /* Type Categories */
  0, /* as number */
  0, /* as sequence */
  0, /* as mapping */
  0, /* hash */
  0, /* binary */
  0, /* repr */
  0, /* getattro */
  0, /* setattro */
  0, /* as buffer */
  0, /* tp_flags */
  py_block_doc,
};

static PyMethodDef Block_methods[] = {
  {"analysis", py_vorbis_analysis,
   METH_VARARGS, py_vorbis_analysis_doc},
  {"addblock", py_vorbis_bitrate_addblock,
   METH_VARARGS, py_vorbis_bitrate_addblock_doc},
  {NULL, NULL}
};

static void
py_block_dealloc(PyObject *self)
{
  vorbis_block_clear(PY_BLOCK(self));
  Py_XDECREF(((py_block *)self)->parent);
  PyMem_DEL(self);
}

static PyObject*
py_block_getattr(PyObject *self, char *name)
{
  return Py_FindMethod(Block_methods, self, name);
}

static PyObject*
py_vorbis_analysis(PyObject *self, PyObject *args)
{
  int ret;
  py_block *b_self = (py_block *) self;

  if (!PyArg_ParseTuple(args, ""))
    return NULL;

  ret = vorbis_analysis(&b_self->vb, NULL);
  if (ret < 0) {
    PyErr_SetString(Py_VorbisError, "vorbis_analysis failure");
    return NULL;
  }
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
py_vorbis_bitrate_addblock(PyObject *self, PyObject *args)
{
  int ret;
  if (!PyArg_ParseTuple(args, ""))
    return NULL;
  ret = vorbis_bitrate_addblock(PY_BLOCK(self));
  if (ret < 0) {
    PyErr_SetString(Py_VorbisError, "addblock failed");
    return NULL;
  }
  Py_INCREF(Py_None);
  return Py_None;
}

PyObject *
py_block_from_block(vorbis_block *vb, PyObject *parent)
{
  py_block *ret = (py_block *) PyObject_NEW(py_block, 
					    &py_block_type);
  if (ret == NULL)
    return NULL;
  
  ret->vb = *vb;
  ret->parent = parent;
  Py_XINCREF(parent);
  return (PyObject *)ret;
}



