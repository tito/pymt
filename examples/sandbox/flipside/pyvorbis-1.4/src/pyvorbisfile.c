#include <stdio.h>
#ifndef _WIN32
#include <assert.h>
#else
#define LITTLE_ENDIAN 0
#define BIG_ENDIAN 1
#define BYTE_ORDER LITTLE_ENDIAN     
#endif

#include "general.h"
#include "vorbismodule.h"
#include "pyvorbisfile.h"
#include "pyvorbisinfo.h"

/*  
*********************************************************
VorbisFile Object methods 
*********************************************************
*/

char py_vorbisfile_doc[] = "";

static void py_ov_file_dealloc(PyObject *);

static PyObject *py_ov_open(py_vorbisfile *, PyObject *);

static char py_ov_read_doc[] = \
"read(length=4096, bigendian=?, word=2, signed=1)\n\
Returns a tuple: (x,y,y)\n\
\twhere x is a buffer object of the data read,\n\
\ty is the number of bytes read,\n\
\tand z is whatever the bitstream value means (no clue).\n\
\n\
length is the number of bytes to read\n\
\tbigendian is the endianness you want (defaults to host endianness)\n\
\tword is the word size\n\tnot sure what signed does\n";

static PyObject *py_ov_read(PyObject *, PyObject *, PyObject *);

FDEF(ov_streams) "Returns the number of logical streams in this VorbisFile";
FDEF(ov_seekable) "Returns whether this VorbisFile is seekable.";
FDEF(ov_bitrate) \
"x.bitrate(stream_idx=-1):\n\n\
Returns the bitrate of this VorbisFile";

FDEF(ov_serialnumber) \
"x.serialnumber(stream_idx=-1):\n\n\
Returns the serialnumber of this VorbisFile.";

FDEF(ov_bitrate_instant) \
     "Returns the bitrate_instant value for this VorbisFile.";

FDEF(ov_raw_total) \
"x.raw_total(stream_idx=-1):\n\n\
Returns the raw_total value for this VorbisFile.";

FDEF(ov_pcm_total) \
"x.pcm_total(stream_idx=-1):\n\n\
Returns the pcm_total value for this VorbisFile.";

FDEF(ov_time_total) \
"x.time_total(stream_idx=-1):\n\n\
Returns the time_total value for this VorbisFile.";

FDEF(ov_raw_seek) "x.raw_seek(pos):\n\nSeeks to raw position pos.";
FDEF(ov_pcm_seek) "x.pcm_seek(pos):\n\nSeeks to pcm position pos.";
FDEF(ov_pcm_seek_page) "x.pcm_seek_page(pos):\n\nSeeks to pcm page pos.";
FDEF(ov_time_seek) "x.time_seek(t):\n\nSeeks to time t";
FDEF(ov_time_seek_page) "x.time_seek_page(pos):\n\nSeeks to time page pos.";
FDEF(ov_raw_tell) "Returns the raw position.";
FDEF(ov_pcm_tell) "Returns the pcm position.";
FDEF(ov_time_tell) "Returns the time position.";
FDEF(ov_info) "Return an info object for this file";

FDEF(ov_comment) \
"x.comment(stream_idx=-1)\n\n\
Returns a dictionary of lists for the comments in this file.\n\
All values are stored in uppercase, since values should be case-insensitive.";

static PyObject *py_ov_file_getattr(PyObject *, char *name);

char OggVorbis_File_Doc[] =
"A VorbisFile object is used to get information about\n\
and read data from an ogg/vorbis file.\n\
\n\
VorbisFile(f) will create a VorbisFile object; f can be\n\
either an open, readable file object or a filename string.\n\
\n\
The most useful method for a VorbisFile object is \"read\".";

PyTypeObject py_vorbisfile_type = {
  PyObject_HEAD_INIT(NULL)
  0,
  "VorbisFile",
  sizeof(py_vorbisfile),
  0,

  /* Standard Methods */
  /* destructor */ py_ov_file_dealloc,
  /* printfunc */ 0,
  /* getattrfunc */ py_ov_file_getattr,
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
  OggVorbis_File_Doc,
};


static PyMethodDef OggVorbis_File_methods[] = {
  {"read", (PyCFunction) py_ov_read, 
   METH_VARARGS | METH_KEYWORDS, py_ov_read_doc},
  {"info", py_ov_info, 
   METH_VARARGS, py_ov_info_doc},
  {"comment", py_ov_comment, 
   METH_VARARGS, py_ov_comment_doc},
  {"streams",  py_ov_streams,  
   METH_VARARGS, py_ov_streams_doc},
  {"seekable",  py_ov_seekable,  
   METH_VARARGS, py_ov_seekable_doc},
  {"bitrate",  py_ov_bitrate,  
   METH_VARARGS, py_ov_bitrate_doc},
  {"serialnumber",  py_ov_serialnumber,  
   METH_VARARGS, py_ov_serialnumber_doc},
  {"bitrate_instant",  py_ov_bitrate_instant,  
   METH_VARARGS, py_ov_bitrate_instant_doc},
  {"raw_total",  py_ov_raw_total,
   METH_VARARGS, py_ov_raw_total_doc},
  {"pcm_total",  py_ov_pcm_total,  
   METH_VARARGS, py_ov_pcm_total_doc},
  {"time_total",  py_ov_time_total, 
   METH_VARARGS, py_ov_time_total_doc},
  {"raw_seek",  py_ov_raw_seek,  
   METH_VARARGS, py_ov_raw_seek_doc},
  {"pcm_seek_page",  py_ov_pcm_seek_page,  
   METH_VARARGS, py_ov_pcm_seek_page_doc},
  {"pcm_seek",  py_ov_pcm_seek,  
   METH_VARARGS, py_ov_pcm_seek_doc},
  {"time_seek",  py_ov_time_seek,  
   METH_VARARGS, py_ov_time_seek_doc},
  {"time_seek_page",  py_ov_time_seek_page,  
   METH_VARARGS, py_ov_time_seek_page_doc},
  {"raw_tell",  py_ov_raw_tell,  
   METH_VARARGS, py_ov_raw_tell_doc},
  {"pcm_tell",  py_ov_pcm_tell,  
   METH_VARARGS, py_ov_pcm_tell_doc},
  {"time_tell",  py_ov_time_tell,  
   METH_VARARGS, py_ov_time_tell_doc},
  {NULL,NULL}
};

PyObject *
py_file_new(PyObject *self, PyObject *args) /* change to accept kwarg */
{ 
  PyObject *ret;
  
  py_vorbisfile *newobj;

  newobj = PyObject_NEW(py_vorbisfile, &py_vorbisfile_type);

  ret = py_ov_open(newobj, args);
  if (ret == NULL) {
    PyMem_DEL(newobj);
    return NULL;
  } else
    Py_DECREF(ret);

  return (PyObject *) newobj;
}

static void
py_ov_file_dealloc(PyObject *self)
{
  if (PY_VORBISFILE(self))
    ov_clear(PY_VORBISFILE(self));

  py_vorbisfile *py_self = (py_vorbisfile *) self;
  if (py_self->py_file) {
    /* If file was opened from a file object, decref it, so it can
       close */
    Py_DECREF(py_self->py_file);
  } else {
    /* Otherwise, we opened the file and should close it. */
    fclose(py_self->c_file);
  }

  PyMem_DEL(self);
}

static PyObject *
py_ov_open(py_vorbisfile *self, PyObject *args)
{
  char *fname;
  char *initial = NULL;
  long ibytes = 0;
  FILE *file;

  PyObject *fobject;
  int retval;
  char errmsg[MSG_SIZE];
  
  if (PyArg_ParseTuple(args, "s|sl", &fname, &initial, &ibytes)) {

    file = fopen(fname, "rb");
    fobject = NULL;

    if (file == NULL) {
      snprintf(errmsg, MSG_SIZE, "Could not open file: %s", fname);
      PyErr_SetString(PyExc_IOError, errmsg);
      return NULL;
    }

  } else {
    PyErr_Clear(); /* clear first failure */
    if (PyArg_ParseTuple(args, "O!|sl", &PyFile_Type, &fobject,
			 &initial, &ibytes)) {
      
      fname = NULL;
      file = PyFile_AsFile(fobject);
      if (!file) 
	return NULL;

      /* We have to duplicate the file descriptor, since both Python
	 and vorbisfile will want to close it. Don't use the file
	 after you pass it in, or much evil will occur. 
	 
	 Really, you shouldn't be passing in files anymore, but in the
	 interest of backwards compatibility it'll stay.
      */
      int orig_fd, new_fd;
      orig_fd = fileno(file);
      new_fd = dup(orig_fd);
      file = fdopen(new_fd, "r");
      if (!file) {
	PyErr_SetString(PyExc_IOError, "Could not duplicate file.");
	return NULL;
      }
    } else {
      PyErr_Clear(); /* clear first failure */
      PyErr_SetString(PyExc_TypeError, 
		      "Argument 1 is not a filename or file object");
      return NULL;
    }
  }

  self->ovf = (OggVorbis_File*) malloc(sizeof(OggVorbis_File));
  self->py_file = fobject;
  Py_XINCREF(fobject); /* Prevent the file from being closed */
  
  retval = ov_open(file, self->ovf, initial, ibytes);

  self->c_file = file;
  if (retval < 0) {
    if (fname != NULL)
      fclose(file);
    Py_XDECREF(self->py_file);

    return v_error_from_code(retval, "Error opening file: ");
  }

  Py_INCREF(Py_None);
  return Py_None;

}

static char *read_kwlist[] = {"length", 
			      "bigendian", 
			      "word", 
			      "signed", 
			      NULL};

static int is_big_endian() {
  static int x = 0x1;
  char x_as_char = *(char *) &x;
  return x_as_char == 0x1 ? 0 : 1;
}

static PyObject *
py_ov_read(PyObject *self, PyObject *args, PyObject *kwdict)
{
  py_vorbisfile * ov_self = (py_vorbisfile *) self;
  PyObject *retobj;
  int retval;

  PyObject *buffobj;
  PyObject *tuple;
  char *buff;
  
  int length, word, sgned, bitstream;
  int bigendianp;

  // Default to host order
  bigendianp = is_big_endian();
  length = 4096;
  word = 2;
  sgned = 1;

  if (!PyArg_ParseTupleAndKeywords(args, kwdict, "|llll", read_kwlist,
                                   &length, &bigendianp, &word, &sgned))
    return NULL;

  buffobj = PyBuffer_New(length);

  tuple = PyTuple_New(1);
  Py_INCREF(buffobj);
  PyTuple_SET_ITEM(tuple, 0, buffobj);

  if (!(PyArg_ParseTuple(tuple, "t#", &buff, &length))) {
    return NULL;
  }
  Py_DECREF(tuple);

  Py_BEGIN_ALLOW_THREADS
    retval = ov_read(ov_self->ovf, buff, length, 
                     bigendianp, word, sgned, &bitstream);
  Py_END_ALLOW_THREADS

    if (retval < 0) {
      Py_DECREF(buffobj);
      return v_error_from_code(retval, "Error reading file: ");
    }

  retobj = Py_BuildValue("Oii", buffobj, retval, bitstream);
  Py_DECREF(buffobj);
  return retobj;
}

static PyObject *
py_ov_streams(PyObject *self, PyObject *args)
{
  py_vorbisfile * ov_self = (py_vorbisfile *) self;
  long val;
  
  if (!PyArg_ParseTuple(args, ""))
    return NULL;

  val = ov_streams(ov_self->ovf);
  return PyInt_FromLong(val);
}

static PyObject *
py_ov_seekable(PyObject *self, PyObject *args)
{
  py_vorbisfile * ov_self = (py_vorbisfile *) self;
  long val;
  
  if (!PyArg_ParseTuple(args, ""))
    return NULL;

  val = ov_seekable(ov_self->ovf);
  return PyInt_FromLong(val);
}

static PyObject *
py_ov_bitrate(PyObject *self, PyObject *args)
{
  py_vorbisfile * ov_self = (py_vorbisfile *) self;
  long val;
  int stream_idx = -1;
  
  if (!PyArg_ParseTuple(args, "|i", &stream_idx))
    return NULL;

  val = ov_bitrate(ov_self->ovf, stream_idx);
  if (val < 0)
    return v_error_from_code(val, "Error getting bitrate: ");
  return PyInt_FromLong(val);
}

static PyObject *
py_ov_serialnumber(PyObject *self, PyObject *args)
{
  py_vorbisfile * ov_self = (py_vorbisfile *) self;
  long val;
  int stream_idx = -1;
  
  if (!PyArg_ParseTuple(args, "|i", &stream_idx)) 
    return NULL;

  val = ov_serialnumber(ov_self->ovf, stream_idx);
  return PyInt_FromLong(val);
}

static PyObject *
py_ov_bitrate_instant(PyObject *self, PyObject *args)
{
  py_vorbisfile * ov_self = (py_vorbisfile *) self;
  long val;

  if (!PyArg_ParseTuple(args, ""))
    return NULL;

  val = ov_bitrate_instant(ov_self->ovf);
  if (val < 0)
    return v_error_from_code(val, "Error getting bitrate_instant: ");
  return PyInt_FromLong(val);
}

static PyObject *
py_ov_raw_total(PyObject *self, PyObject *args)
{
  py_vorbisfile * ov_self = (py_vorbisfile *) self;
  ogg_int64_t val;
  int stream_idx = -1;

  if (!PyArg_ParseTuple(args, "|i", &stream_idx)) 
    return NULL;

  val = ov_raw_total(ov_self->ovf, stream_idx);
  if (val < 0)
    return v_error_from_code(val, "Error in ov_raw_total: ");
  return PyLong_FromLongLong(val);
}

static PyObject *
py_ov_pcm_total(PyObject *self, PyObject *args)
{
  py_vorbisfile * ov_self = (py_vorbisfile *) self;
  ogg_int64_t val;
  int stream_idx = -1;

  if (!PyArg_ParseTuple(args, "|i", &stream_idx)) 
    return NULL;

  val = ov_pcm_total(ov_self->ovf, stream_idx);
  if (val < 0)
    return v_error_from_code(val, "Error in ov_pcm_total: ");
  return PyLong_FromLongLong(val);
}

static PyObject *
py_ov_time_total(PyObject *self, PyObject *args)
{
  py_vorbisfile * ov_self = (py_vorbisfile *) self;
  double val;
  int stream_idx = -1;

  if (!PyArg_ParseTuple(args, "|i", &stream_idx))
    return NULL;

  val = ov_time_total(ov_self->ovf, stream_idx);
  if (val < 0)
    return v_error_from_code(val, "Error in ov_time_total: ");
  return PyFloat_FromDouble(val);
}

static PyObject *
py_ov_raw_seek(PyObject *self, PyObject *args)
{
  py_vorbisfile * ov_self = (py_vorbisfile *) self;
  int val;
  long pos;

  if (!PyArg_ParseTuple(args, "l", &pos)) 
    return NULL;

  val = ov_raw_seek(ov_self->ovf, pos);
  RETURN_IF_VAL(val, "Error in ov_raw_seek");
}

static PyObject *
py_ov_pcm_seek(PyObject *self, PyObject *args)
{
  py_vorbisfile * ov_self = (py_vorbisfile *) self;
  PyObject *longobj;
  int val;
  ogg_int64_t pos;

  if (!PyArg_ParseTuple(args, "O", &longobj))
    return NULL;
 
  if (!modinfo->arg_to_int64(longobj, &pos))
    return NULL;

  val = ov_pcm_seek(ov_self->ovf, pos);
  RETURN_IF_VAL(val, "Error is ov_pcm_seek");
}

static PyObject *
py_ov_pcm_seek_page(PyObject *self, PyObject *args)
{
  py_vorbisfile * ov_self = (py_vorbisfile *) self;
  int val;
  PyObject *longobj;
  ogg_int64_t pos;

  if (!PyArg_ParseTuple(args, "O", &longobj)) 
    return NULL;

  if (!modinfo->arg_to_int64(longobj, &pos))
    return NULL;

  val = ov_pcm_seek_page(ov_self->ovf, pos);
  RETURN_IF_VAL(val, "Error is ov_pcm_seek_page");
}

static PyObject *
py_ov_time_seek(PyObject *self, PyObject *args)
{
  py_vorbisfile * ov_self = (py_vorbisfile *) self;
  int val;
  double pos;

  if (!PyArg_ParseTuple(args, "d", &pos)) 
    return NULL;

  val = ov_time_seek(ov_self->ovf, pos);
  RETURN_IF_VAL(val, "Error is ov_pcm_time_seek");
}

static PyObject *
py_ov_time_seek_page(PyObject *self, PyObject *args)
{
  py_vorbisfile * ov_self = (py_vorbisfile *) self;
  int val;
  double pos;

  if (!PyArg_ParseTuple(args, "d", &pos)) 
    return NULL;

  val = ov_time_seek_page(ov_self->ovf, pos);
  RETURN_IF_VAL(val, "Error is ov_pcm_time_seek_page");
}

static PyObject *
py_ov_raw_tell(PyObject *self, PyObject *args)
{
  py_vorbisfile * ov_self = (py_vorbisfile *) self;
  ogg_int64_t val;

  if (!PyArg_ParseTuple(args, ""))
    return NULL;

  val = ov_raw_tell(ov_self->ovf);
  return PyLong_FromLongLong(val);
}

static PyObject *
py_ov_pcm_tell(PyObject *self, PyObject *args)
{
  py_vorbisfile * ov_self = (py_vorbisfile *) self;
  ogg_int64_t val;
  
  if (!PyArg_ParseTuple(args, ""))
    return NULL;

  val = ov_pcm_tell(ov_self->ovf);
  return PyLong_FromLongLong(val);
}

static PyObject *
py_ov_time_tell(PyObject *self, PyObject *args)
{
  py_vorbisfile * ov_self = (py_vorbisfile *) self;
  double val;
  
  if (!PyArg_ParseTuple(args, ""))
    return NULL;

  val = ov_time_tell(ov_self->ovf);
  return PyFloat_FromDouble(val);
}

static PyObject*
py_ov_info(PyObject *self, PyObject *args)
{
  py_vorbisfile *ov_self = (py_vorbisfile *) self;
  int stream_idx = -1;
  vorbis_info *vi;

  if (!PyArg_ParseTuple(args, "|i", &stream_idx))
    return NULL;

  vi = ov_info(ov_self->ovf, stream_idx);
  if (!vi) {
    PyErr_SetString(PyExc_RuntimeError, "Couldn't get info for VorbisFile.");
    return NULL;
  }
  
  return py_info_new_from_vi(vi);
}


static PyObject *
py_ov_comment(PyObject *self, PyObject *args)
{
  py_vorbisfile *ov_self = (py_vorbisfile *) self;
  vorbis_comment *comments;

  int stream_idx = -1;
  
  if (!PyArg_ParseTuple(args, "|i", &stream_idx))
    return NULL;

  comments = ov_comment(ov_self->ovf, stream_idx);
  if (!comments) {
    PyErr_SetString(PyExc_RuntimeError, "Couldn't get comments");
    return NULL;
  }

  return py_comment_new_from_vc(comments, self);
}

static PyObject*
py_ov_file_getattr(PyObject *self, char *name)
{
  return Py_FindMethod(OggVorbis_File_methods, self, name);
}




