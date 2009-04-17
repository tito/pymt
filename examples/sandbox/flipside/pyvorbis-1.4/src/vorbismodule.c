#include <vorbis/codec.h>
#include <stdio.h>

#include "vorbismodule.h"

#include "pyvorbiscodec.h"
#include "pyvorbisfile.h"
#include "pyvorbisinfo.h"

#include "general.h"

static PyMethodDef Vorbis_methods[] = {
  {"VorbisFile", py_file_new, 
   METH_VARARGS, py_vorbisfile_doc},
  {"VorbisInfo", (PyCFunction) py_info_new, 
   METH_VARARGS | METH_KEYWORDS, py_vinfo_doc},
  {"VorbisComment", py_comment_new, 
   METH_VARARGS, py_vcomment_doc},
  {NULL, NULL}
};

static char docstring[] = "";
PyObject *
v_error_from_code(int code, char *msg)
{
  char errmsg[MSG_SIZE];
  char *reason;

  switch (code) {
  case OV_FALSE: 
    reason = "Function returned FALSE.";
    break;
  case OV_HOLE: 
    reason = "Interruption in data.";
    break;
  case OV_EREAD: 
    reason = "Read error.";
    break;
  case OV_EFAULT: 
    reason = "Internal logic fault. Bug or heap/stack corruption.";
    break;
  case OV_EIMPL: 
    reason = "Bitstream uses unimplemented feature.";
    break;
  case OV_EINVAL: 
    reason = "Invalid argument.";
    break;
  case OV_ENOTVORBIS: 
    reason = "Data is not Vorbis data.";
      break;
  case OV_EBADHEADER: 
    reason = "Invalid Vorbis bitstream header.";
    break;
  case OV_EVERSION: 
    reason = "Vorbis version mismatch.";
    break;
  case OV_ENOTAUDIO: 
    reason = "Packet data is not audio.";
    break;
  case OV_EBADPACKET: 
    reason = "Invalid packet.";
    break;
  case OV_EBADLINK: 
    reason = "Invalid stream section, or the requested link is corrupt.";
    break;
  case OV_ENOSEEK: 
    reason = "Bitstream is not seekable.";
    break;
  default:
      reason = "Unknown error.";
  }

  strncpy(errmsg, msg, MSG_SIZE);
  strncat(errmsg, reason, MSG_SIZE - strlen(errmsg));
  PyErr_SetString(Py_VorbisError, errmsg);
  return NULL;
}

ogg_module_info *modinfo;

void 
initvorbis(void)
{
  PyObject *module, *dict;

  py_dsp_type.ob_type = &PyType_Type;
  py_block_type.ob_type = &PyType_Type;
  py_vorbisfile_type.ob_type = &PyType_Type;
  py_vinfo_type.ob_type = &PyType_Type;
  py_vcomment_type.ob_type = &PyType_Type;

  module = Py_InitModule("ogg.vorbis", Vorbis_methods);
  dict = PyModule_GetDict(module);
  
  modinfo = PyCObject_Import("ogg._ogg", "_moduleinfo");
  if (modinfo == NULL) {
    PyErr_SetString(PyExc_ImportError, "Could not load ogg._ogg");
    return;
  }
  Py_VorbisError = PyErr_NewException("ogg.vorbis.VorbisError", 
				      modinfo->Py_OggError, NULL);
  PyDict_SetItemString(dict, "VorbisError", 
		       Py_VorbisError);
  
  PyDict_SetItemString(dict, "__doc__", 
		       PyString_FromString(docstring));

  PyDict_SetItemString(dict, "__version__", 
		       PyString_FromString("1.2"));

  if (PyErr_Occurred())
    PyErr_SetString(PyExc_ImportError, 
		    "ogg.vorbis: init failed");
}

