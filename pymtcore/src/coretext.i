%{
#include "coretext.h"
%}

%feature("shadow") CoreText::draw() %{
def draw(*args): return $action(*args)
if _newclass:label = property(_get_label, _set_label)
__swig_setmethods__["label"] = _pymtcore.CoreText__set_label
__swig_getmethods__["label"] = _pymtcore.CoreText__get_label
if _newclass:fontname = property(_get_fontname, _set_fontname)
__swig_setmethods__["fontname"] = _pymtcore.CoreText__set_fontname
__swig_getmethods__["fontname"] = _pymtcore.CoreText__get_fontname
if _newclass:fontsize = property(_get_fontsize, _set_fontsize)
__swig_setmethods__["fontsize"] = _pymtcore.CoreText__set_fontsize
__swig_getmethods__["fontsize"] = _pymtcore.CoreText__get_fontsize
if _newclass:bold = property(_get_bold, _set_bold)
__swig_setmethods__["bold"] = _pymtcore.CoreText__set_bold
__swig_getmethods__["bold"] = _pymtcore.CoreText__get_bold
if _newclass:multiline = property(_get_multiline, _set_multiline)
__swig_setmethods__["multiline"] = _pymtcore.CoreText__set_multiline
__swig_getmethods__["multiline"] = _pymtcore.CoreText__get_multiline
%}

%include "coretext.h"

