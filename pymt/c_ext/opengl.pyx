import struct, array
cimport c_opengl


ctypedef  void     	        GLvoid
ctypedef  char              GLchar
ctypedef  unsigned int      GLenum
ctypedef  unsigned char     GLboolean
ctypedef  unsigned int      GLbitfield
ctypedef  short             GLshort
ctypedef  int               GLint
ctypedef  int               GLsizei
ctypedef  unsigned short    GLushort
ctypedef  unsigned int      GLuint
ctypedef  signed   char     GLbyte
ctypedef  unsigned   char   GLubyte
ctypedef  float             GLfloat
ctypedef  float             GLclampf
ctypedef  int               GLfixed
ctypedef  signed long int   GLintptr
ctypedef  signed long int   GLsizeiptr


GL_ES_VERSION_2_0 = c_opengl.GL_ES_VERSION_2_0
GL_DEPTH_BUFFER_BIT = c_opengl.GL_DEPTH_BUFFER_BIT
GL_STENCIL_BUFFER_BIT = c_opengl.GL_STENCIL_BUFFER_BIT
GL_COLOR_BUFFER_BIT = c_opengl.GL_COLOR_BUFFER_BIT
GL_FALSE = c_opengl.GL_FALSE
GL_TRUE = c_opengl.GL_TRUE
GL_POINTS = c_opengl.GL_POINTS
GL_LINES = c_opengl.GL_LINES
GL_LINE_LOOP = c_opengl.GL_LINE_LOOP
GL_LINE_STRIP = c_opengl.GL_LINE_STRIP
GL_TRIANGLES = c_opengl.GL_TRIANGLES
GL_TRIANGLE_STRIP = c_opengl.GL_TRIANGLE_STRIP
GL_TRIANGLE_FAN = c_opengl.GL_TRIANGLE_FAN
GL_ZERO = c_opengl.GL_ZERO
GL_ONE = c_opengl.GL_ONE
GL_SRC_COLOR = c_opengl.GL_SRC_COLOR
GL_ONE_MINUS_SRC_COLOR = c_opengl.GL_ONE_MINUS_SRC_COLOR
GL_SRC_ALPHA = c_opengl.GL_SRC_ALPHA
GL_ONE_MINUS_SRC_ALPHA = c_opengl.GL_ONE_MINUS_SRC_ALPHA
GL_DST_ALPHA = c_opengl.GL_DST_ALPHA
GL_ONE_MINUS_DST_ALPHA = c_opengl.GL_ONE_MINUS_DST_ALPHA
GL_DST_COLOR = c_opengl.GL_DST_COLOR
GL_ONE_MINUS_DST_COLOR = c_opengl.GL_ONE_MINUS_DST_COLOR
GL_SRC_ALPHA_SATURATE = c_opengl.GL_SRC_ALPHA_SATURATE
GL_FUNC_ADD = c_opengl.GL_FUNC_ADD
GL_BLEND_EQUATION = c_opengl.GL_BLEND_EQUATION
GL_BLEND_EQUATION_RGB = c_opengl.GL_BLEND_EQUATION_RGB
GL_BLEND_EQUATION_ALPHA = c_opengl.GL_BLEND_EQUATION_ALPHA
GL_FUNC_SUBTRACT = c_opengl.GL_FUNC_SUBTRACT
GL_FUNC_REVERSE_SUBTRACT = c_opengl.GL_FUNC_REVERSE_SUBTRACT
GL_BLEND_DST_RGB = c_opengl.GL_BLEND_DST_RGB
GL_BLEND_SRC_RGB = c_opengl.GL_BLEND_SRC_RGB
GL_BLEND_DST_ALPHA = c_opengl.GL_BLEND_DST_ALPHA
GL_BLEND_SRC_ALPHA = c_opengl.GL_BLEND_SRC_ALPHA
GL_ANT_COLOR = c_opengl.GL_ANT_COLOR
GL_ONE_MINUS_ANT_COLOR = c_opengl.GL_ONE_MINUS_ANT_COLOR
GL_ANT_ALPHA = c_opengl.GL_ANT_ALPHA
GL_ONE_MINUS_ANT_ALPHA = c_opengl.GL_ONE_MINUS_ANT_ALPHA
GL_BLEND_COLOR = c_opengl.GL_BLEND_COLOR
GL_ARRAY_BUFFER = c_opengl.GL_ARRAY_BUFFER
GL_ELEMENT_ARRAY_BUFFER = c_opengl.GL_ELEMENT_ARRAY_BUFFER
GL_ARRAY_BUFFER_BINDING = c_opengl.GL_ARRAY_BUFFER_BINDING
GL_ELEMENT_ARRAY_BUFFER_BINDING = c_opengl.GL_ELEMENT_ARRAY_BUFFER_BINDING
GL_STREAM_DRAW = c_opengl.GL_STREAM_DRAW
GL_STATIC_DRAW = c_opengl.GL_STATIC_DRAW
GL_DYNAMIC_DRAW = c_opengl.GL_DYNAMIC_DRAW
GL_BUFFER_SIZE = c_opengl.GL_BUFFER_SIZE
GL_BUFFER_USAGE = c_opengl.GL_BUFFER_USAGE
GL_CURRENT_VERTEX_ATTRIB = c_opengl.GL_CURRENT_VERTEX_ATTRIB
GL_FRONT = c_opengl.GL_FRONT
GL_BACK = c_opengl.GL_BACK
GL_FRONT_AND_BACK = c_opengl.GL_FRONT_AND_BACK
GL_TEXTURE_2D = c_opengl.GL_TEXTURE_2D
GL_CULL_FACE = c_opengl.GL_CULL_FACE
GL_BLEND = c_opengl.GL_BLEND
GL_DITHER = c_opengl.GL_DITHER
GL_STENCIL_TEST = c_opengl.GL_STENCIL_TEST
GL_DEPTH_TEST = c_opengl.GL_DEPTH_TEST
GL_SCISSOR_TEST = c_opengl.GL_SCISSOR_TEST
GL_POLYGON_OFFSET_FILL = c_opengl.GL_POLYGON_OFFSET_FILL
GL_SAMPLE_ALPHA_TO_COVERAGE = c_opengl.GL_SAMPLE_ALPHA_TO_COVERAGE
GL_SAMPLE_COVERAGE = c_opengl.GL_SAMPLE_COVERAGE
GL_NO_ERROR = c_opengl.GL_NO_ERROR
GL_INVALID_ENUM = c_opengl.GL_INVALID_ENUM
GL_INVALID_VALUE = c_opengl.GL_INVALID_VALUE
GL_INVALID_OPERATION = c_opengl.GL_INVALID_OPERATION
GL_OUT_OF_MEMORY = c_opengl.GL_OUT_OF_MEMORY
GL_CW = c_opengl.GL_CW
GL_CCW = c_opengl.GL_CCW
GL_LINE_WIDTH = c_opengl.GL_LINE_WIDTH
GL_ALIASED_POINT_SIZE_RANGE = c_opengl.GL_ALIASED_POINT_SIZE_RANGE
GL_ALIASED_LINE_WIDTH_RANGE = c_opengl.GL_ALIASED_LINE_WIDTH_RANGE
GL_CULL_FACE_MODE = c_opengl.GL_CULL_FACE_MODE
GL_FRONT_FACE = c_opengl.GL_FRONT_FACE
GL_DEPTH_RANGE = c_opengl.GL_DEPTH_RANGE
GL_DEPTH_WRITEMASK = c_opengl.GL_DEPTH_WRITEMASK
GL_DEPTH_CLEAR_VALUE = c_opengl.GL_DEPTH_CLEAR_VALUE
GL_DEPTH_FUNC = c_opengl.GL_DEPTH_FUNC
GL_STENCIL_CLEAR_VALUE = c_opengl.GL_STENCIL_CLEAR_VALUE
GL_STENCIL_FUNC = c_opengl.GL_STENCIL_FUNC
GL_STENCIL_FAIL = c_opengl.GL_STENCIL_FAIL
GL_STENCIL_PASS_DEPTH_FAIL = c_opengl.GL_STENCIL_PASS_DEPTH_FAIL
GL_STENCIL_PASS_DEPTH_PASS = c_opengl.GL_STENCIL_PASS_DEPTH_PASS
GL_STENCIL_REF = c_opengl.GL_STENCIL_REF
GL_STENCIL_VALUE_MASK = c_opengl.GL_STENCIL_VALUE_MASK
GL_STENCIL_WRITEMASK = c_opengl.GL_STENCIL_WRITEMASK
GL_STENCIL_BACK_FUNC = c_opengl.GL_STENCIL_BACK_FUNC
GL_STENCIL_BACK_FAIL = c_opengl.GL_STENCIL_BACK_FAIL
GL_STENCIL_BACK_PASS_DEPTH_FAIL = c_opengl.GL_STENCIL_BACK_PASS_DEPTH_FAIL
GL_STENCIL_BACK_PASS_DEPTH_PASS = c_opengl.GL_STENCIL_BACK_PASS_DEPTH_PASS
GL_STENCIL_BACK_REF = c_opengl.GL_STENCIL_BACK_REF
GL_STENCIL_BACK_VALUE_MASK = c_opengl.GL_STENCIL_BACK_VALUE_MASK
GL_STENCIL_BACK_WRITEMASK = c_opengl.GL_STENCIL_BACK_WRITEMASK
GL_VIEWPORT = c_opengl.GL_VIEWPORT
GL_SCISSOR_BOX = c_opengl.GL_SCISSOR_BOX
GL_COLOR_CLEAR_VALUE = c_opengl.GL_COLOR_CLEAR_VALUE
GL_COLOR_WRITEMASK = c_opengl.GL_COLOR_WRITEMASK
GL_UNPACK_ALIGNMENT = c_opengl.GL_UNPACK_ALIGNMENT
GL_PACK_ALIGNMENT = c_opengl.GL_PACK_ALIGNMENT
GL_MAX_TEXTURE_SIZE = c_opengl.GL_MAX_TEXTURE_SIZE
GL_MAX_VIEWPORT_DIMS = c_opengl.GL_MAX_VIEWPORT_DIMS
GL_SUBPIXEL_BITS = c_opengl.GL_SUBPIXEL_BITS
GL_RED_BITS = c_opengl.GL_RED_BITS
GL_GREEN_BITS = c_opengl.GL_GREEN_BITS
GL_BLUE_BITS = c_opengl.GL_BLUE_BITS
GL_ALPHA_BITS = c_opengl.GL_ALPHA_BITS
GL_DEPTH_BITS = c_opengl.GL_DEPTH_BITS
GL_STENCIL_BITS = c_opengl.GL_STENCIL_BITS
GL_POLYGON_OFFSET_UNITS = c_opengl.GL_POLYGON_OFFSET_UNITS
GL_POLYGON_OFFSET_FACTOR = c_opengl.GL_POLYGON_OFFSET_FACTOR
GL_TEXTURE_BINDING_2D = c_opengl.GL_TEXTURE_BINDING_2D
GL_SAMPLE_BUFFERS = c_opengl.GL_SAMPLE_BUFFERS
GL_SAMPLES = c_opengl.GL_SAMPLES
GL_SAMPLE_COVERAGE_VALUE = c_opengl.GL_SAMPLE_COVERAGE_VALUE
GL_SAMPLE_COVERAGE_INVERT = c_opengl.GL_SAMPLE_COVERAGE_INVERT
GL_NUM_COMPRESSED_TEXTURE_FORMATS = c_opengl.GL_NUM_COMPRESSED_TEXTURE_FORMATS
GL_COMPRESSED_TEXTURE_FORMATS = c_opengl.GL_COMPRESSED_TEXTURE_FORMATS
GL_DONT_CARE = c_opengl.GL_DONT_CARE
GL_FASTEST = c_opengl.GL_FASTEST
GL_NICEST = c_opengl.GL_NICEST
GL_GENERATE_MIPMAP_HINT = c_opengl.GL_GENERATE_MIPMAP_HINT
GL_BYTE = c_opengl.GL_BYTE
GL_UNSIGNED_BYTE = c_opengl.GL_UNSIGNED_BYTE
GL_SHORT = c_opengl.GL_SHORT
GL_UNSIGNED_SHORT = c_opengl.GL_UNSIGNED_SHORT
GL_INT = c_opengl.GL_INT
GL_UNSIGNED_INT = c_opengl.GL_UNSIGNED_INT
GL_FLOAT = c_opengl.GL_FLOAT
GL_FIXED = c_opengl.GL_FIXED
GL_DEPTH_COMPONENT = c_opengl.GL_DEPTH_COMPONENT
GL_ALPHA = c_opengl.GL_ALPHA
GL_RGB = c_opengl.GL_RGB
GL_RGBA = c_opengl.GL_RGBA
GL_LUMINANCE = c_opengl.GL_LUMINANCE
GL_LUMINANCE_ALPHA = c_opengl.GL_LUMINANCE_ALPHA
GL_UNSIGNED_SHORT_4_4_4_4 = c_opengl.GL_UNSIGNED_SHORT_4_4_4_4
GL_UNSIGNED_SHORT_5_5_5_1 = c_opengl.GL_UNSIGNED_SHORT_5_5_5_1
GL_UNSIGNED_SHORT_5_6_5 = c_opengl.GL_UNSIGNED_SHORT_5_6_5
GL_FRAGMENT_SHADER = c_opengl.GL_FRAGMENT_SHADER
GL_VERTEX_SHADER = c_opengl.GL_VERTEX_SHADER
GL_MAX_VERTEX_ATTRIBS = c_opengl.GL_MAX_VERTEX_ATTRIBS
GL_MAX_VERTEX_UNIFORM_VECTORS = c_opengl.GL_MAX_VERTEX_UNIFORM_VECTORS
GL_MAX_VARYING_VECTORS = c_opengl.GL_MAX_VARYING_VECTORS
GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS = c_opengl.GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS
GL_MAX_VERTEX_TEXTURE_IMAGE_UNITS = c_opengl.GL_MAX_VERTEX_TEXTURE_IMAGE_UNITS
GL_MAX_TEXTURE_IMAGE_UNITS = c_opengl.GL_MAX_TEXTURE_IMAGE_UNITS
GL_MAX_FRAGMENT_UNIFORM_VECTORS = c_opengl.GL_MAX_FRAGMENT_UNIFORM_VECTORS
GL_SHADER_TYPE = c_opengl.GL_SHADER_TYPE
GL_DELETE_STATUS = c_opengl.GL_DELETE_STATUS
GL_LINK_STATUS = c_opengl.GL_LINK_STATUS
GL_VALIDATE_STATUS = c_opengl.GL_VALIDATE_STATUS
GL_ATTACHED_SHADERS = c_opengl.GL_ATTACHED_SHADERS
GL_ACTIVE_UNIFORMS = c_opengl.GL_ACTIVE_UNIFORMS
GL_ACTIVE_UNIFORM_MAX_LENGTH = c_opengl.GL_ACTIVE_UNIFORM_MAX_LENGTH
GL_ACTIVE_ATTRIBUTES = c_opengl.GL_ACTIVE_ATTRIBUTES
GL_ACTIVE_ATTRIBUTE_MAX_LENGTH = c_opengl.GL_ACTIVE_ATTRIBUTE_MAX_LENGTH
GL_SHADING_LANGUAGE_VERSION = c_opengl.GL_SHADING_LANGUAGE_VERSION
GL_CURRENT_PROGRAM = c_opengl.GL_CURRENT_PROGRAM
GL_NEVER = c_opengl.GL_NEVER
GL_LESS = c_opengl.GL_LESS
GL_EQUAL = c_opengl.GL_EQUAL
GL_LEQUAL = c_opengl.GL_LEQUAL
GL_GREATER = c_opengl.GL_GREATER
GL_NOTEQUAL = c_opengl.GL_NOTEQUAL
GL_GEQUAL = c_opengl.GL_GEQUAL
GL_ALWAYS = c_opengl.GL_ALWAYS
GL_KEEP = c_opengl.GL_KEEP
GL_REPLACE = c_opengl.GL_REPLACE
GL_INCR = c_opengl.GL_INCR
GL_DECR = c_opengl.GL_DECR
GL_INVERT = c_opengl.GL_INVERT
GL_INCR_WRAP = c_opengl.GL_INCR_WRAP
GL_DECR_WRAP = c_opengl.GL_DECR_WRAP
GL_VENDOR = c_opengl.GL_VENDOR
GL_RENDERER = c_opengl.GL_RENDERER
GL_VERSION = c_opengl.GL_VERSION
GL_EXTENSIONS = c_opengl.GL_EXTENSIONS
GL_NEAREST = c_opengl.GL_NEAREST
GL_LINEAR = c_opengl.GL_LINEAR
GL_NEAREST_MIPMAP_NEAREST = c_opengl.GL_NEAREST_MIPMAP_NEAREST
GL_LINEAR_MIPMAP_NEAREST = c_opengl.GL_LINEAR_MIPMAP_NEAREST
GL_NEAREST_MIPMAP_LINEAR = c_opengl.GL_NEAREST_MIPMAP_LINEAR
GL_LINEAR_MIPMAP_LINEAR = c_opengl.GL_LINEAR_MIPMAP_LINEAR
GL_TEXTURE_MAG_FILTER = c_opengl.GL_TEXTURE_MAG_FILTER
GL_TEXTURE_MIN_FILTER = c_opengl.GL_TEXTURE_MIN_FILTER
GL_TEXTURE_WRAP_S = c_opengl.GL_TEXTURE_WRAP_S
GL_TEXTURE_WRAP_T = c_opengl.GL_TEXTURE_WRAP_T
GL_TEXTURE = c_opengl.GL_TEXTURE
GL_TEXTURE_CUBE_MAP = c_opengl.GL_TEXTURE_CUBE_MAP
GL_TEXTURE_BINDING_CUBE_MAP = c_opengl.GL_TEXTURE_BINDING_CUBE_MAP
GL_TEXTURE_CUBE_MAP_POSITIVE_X = c_opengl.GL_TEXTURE_CUBE_MAP_POSITIVE_X
GL_TEXTURE_CUBE_MAP_NEGATIVE_X = c_opengl.GL_TEXTURE_CUBE_MAP_NEGATIVE_X
GL_TEXTURE_CUBE_MAP_POSITIVE_Y = c_opengl.GL_TEXTURE_CUBE_MAP_POSITIVE_Y
GL_TEXTURE_CUBE_MAP_NEGATIVE_Y = c_opengl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Y
GL_TEXTURE_CUBE_MAP_POSITIVE_Z = c_opengl.GL_TEXTURE_CUBE_MAP_POSITIVE_Z
GL_TEXTURE_CUBE_MAP_NEGATIVE_Z = c_opengl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Z
GL_MAX_CUBE_MAP_TEXTURE_SIZE = c_opengl.GL_MAX_CUBE_MAP_TEXTURE_SIZE
GL_TEXTURE0 = c_opengl.GL_TEXTURE0
GL_TEXTURE1 = c_opengl.GL_TEXTURE1
GL_TEXTURE2 = c_opengl.GL_TEXTURE2
GL_TEXTURE3 = c_opengl.GL_TEXTURE3
GL_TEXTURE4 = c_opengl.GL_TEXTURE4
GL_TEXTURE5 = c_opengl.GL_TEXTURE5
GL_TEXTURE6 = c_opengl.GL_TEXTURE6
GL_TEXTURE7 = c_opengl.GL_TEXTURE7
GL_TEXTURE8 = c_opengl.GL_TEXTURE8
GL_TEXTURE9 = c_opengl.GL_TEXTURE9
GL_TEXTURE10 = c_opengl.GL_TEXTURE10
GL_TEXTURE11 = c_opengl.GL_TEXTURE11
GL_TEXTURE12 = c_opengl.GL_TEXTURE12
GL_TEXTURE13 = c_opengl.GL_TEXTURE13
GL_TEXTURE14 = c_opengl.GL_TEXTURE14
GL_TEXTURE15 = c_opengl.GL_TEXTURE15
GL_TEXTURE16 = c_opengl.GL_TEXTURE16
GL_TEXTURE17 = c_opengl.GL_TEXTURE17
GL_TEXTURE18 = c_opengl.GL_TEXTURE18
GL_TEXTURE19 = c_opengl.GL_TEXTURE19
GL_TEXTURE20 = c_opengl.GL_TEXTURE20
GL_TEXTURE21 = c_opengl.GL_TEXTURE21
GL_TEXTURE22 = c_opengl.GL_TEXTURE22
GL_TEXTURE23 = c_opengl.GL_TEXTURE23
GL_TEXTURE24 = c_opengl.GL_TEXTURE24
GL_TEXTURE25 = c_opengl.GL_TEXTURE25
GL_TEXTURE26 = c_opengl.GL_TEXTURE26
GL_TEXTURE27 = c_opengl.GL_TEXTURE27
GL_TEXTURE28 = c_opengl.GL_TEXTURE28
GL_TEXTURE29 = c_opengl.GL_TEXTURE29
GL_TEXTURE30 = c_opengl.GL_TEXTURE30
GL_TEXTURE31 = c_opengl.GL_TEXTURE31
GL_ACTIVE_TEXTURE = c_opengl.GL_ACTIVE_TEXTURE
GL_REPEAT = c_opengl.GL_REPEAT
GL_CLAMP_TO_EDGE = c_opengl.GL_CLAMP_TO_EDGE
GL_MIRRORED_REPEAT = c_opengl.GL_MIRRORED_REPEAT
GL_FLOAT_VEC2 = c_opengl.GL_FLOAT_VEC2
GL_FLOAT_VEC3 = c_opengl.GL_FLOAT_VEC3
GL_FLOAT_VEC4 = c_opengl.GL_FLOAT_VEC4
GL_INT_VEC2 = c_opengl.GL_INT_VEC2
GL_INT_VEC3 = c_opengl.GL_INT_VEC3
GL_INT_VEC4 = c_opengl.GL_INT_VEC4
GL_BOOL = c_opengl.GL_BOOL
GL_BOOL_VEC2 = c_opengl.GL_BOOL_VEC2
GL_BOOL_VEC3 = c_opengl.GL_BOOL_VEC3
GL_BOOL_VEC4 = c_opengl.GL_BOOL_VEC4
GL_FLOAT_MAT2 = c_opengl.GL_FLOAT_MAT2
GL_FLOAT_MAT3 = c_opengl.GL_FLOAT_MAT3
GL_FLOAT_MAT4 = c_opengl.GL_FLOAT_MAT4
GL_SAMPLER_2D = c_opengl.GL_SAMPLER_2D
GL_SAMPLER_CUBE = c_opengl.GL_SAMPLER_CUBE
GL_VERTEX_ATTRIB_ARRAY_ENABLED = c_opengl.GL_VERTEX_ATTRIB_ARRAY_ENABLED
GL_VERTEX_ATTRIB_ARRAY_SIZE = c_opengl.GL_VERTEX_ATTRIB_ARRAY_SIZE
GL_VERTEX_ATTRIB_ARRAY_STRIDE = c_opengl.GL_VERTEX_ATTRIB_ARRAY_STRIDE
GL_VERTEX_ATTRIB_ARRAY_TYPE = c_opengl.GL_VERTEX_ATTRIB_ARRAY_TYPE
GL_VERTEX_ATTRIB_ARRAY_NORMALIZED = c_opengl.GL_VERTEX_ATTRIB_ARRAY_NORMALIZED
GL_VERTEX_ATTRIB_ARRAY_POINTER = c_opengl.GL_VERTEX_ATTRIB_ARRAY_POINTER
GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING = c_opengl.GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING
GL_IMPLEMENTATION_COLOR_READ_TYPE = c_opengl.GL_IMPLEMENTATION_COLOR_READ_TYPE
GL_IMPLEMENTATION_COLOR_READ_FORMAT = c_opengl.GL_IMPLEMENTATION_COLOR_READ_FORMAT
GL_COMPILE_STATUS = c_opengl.GL_COMPILE_STATUS
GL_INFO_LOG_LENGTH = c_opengl.GL_INFO_LOG_LENGTH
GL_SHADER_SOURCE_LENGTH = c_opengl.GL_SHADER_SOURCE_LENGTH
GL_SHADER_COMPILER = c_opengl.GL_SHADER_COMPILER
GL_SHADER_BINARY_FORMATS = c_opengl.GL_SHADER_BINARY_FORMATS
GL_NUM_SHADER_BINARY_FORMATS = c_opengl.GL_NUM_SHADER_BINARY_FORMATS
GL_LOW_FLOAT = c_opengl.GL_LOW_FLOAT
GL_MEDIUM_FLOAT = c_opengl.GL_MEDIUM_FLOAT
GL_HIGH_FLOAT = c_opengl.GL_HIGH_FLOAT
GL_LOW_INT = c_opengl.GL_LOW_INT
GL_MEDIUM_INT = c_opengl.GL_MEDIUM_INT
GL_HIGH_INT = c_opengl.GL_HIGH_INT
GL_FRAMEBUFFER = c_opengl.GL_FRAMEBUFFER
GL_RENDERBUFFER = c_opengl.GL_RENDERBUFFER
GL_RGBA4 = c_opengl.GL_RGBA4
GL_RGB5_A1 = c_opengl.GL_RGB5_A1
GL_RGB565 = c_opengl.GL_RGB565
GL_DEPTH_COMPONENT16 = c_opengl.GL_DEPTH_COMPONENT16
GL_STENCIL_INDEX = c_opengl.GL_STENCIL_INDEX
GL_STENCIL_INDEX8 = c_opengl.GL_STENCIL_INDEX8
GL_RENDERBUFFER_WIDTH = c_opengl.GL_RENDERBUFFER_WIDTH
GL_RENDERBUFFER_HEIGHT = c_opengl.GL_RENDERBUFFER_HEIGHT
GL_RENDERBUFFER_INTERNAL_FORMAT = c_opengl.GL_RENDERBUFFER_INTERNAL_FORMAT
GL_RENDERBUFFER_RED_SIZE = c_opengl.GL_RENDERBUFFER_RED_SIZE
GL_RENDERBUFFER_GREEN_SIZE = c_opengl.GL_RENDERBUFFER_GREEN_SIZE
GL_RENDERBUFFER_BLUE_SIZE = c_opengl.GL_RENDERBUFFER_BLUE_SIZE
GL_RENDERBUFFER_ALPHA_SIZE = c_opengl.GL_RENDERBUFFER_ALPHA_SIZE
GL_RENDERBUFFER_DEPTH_SIZE = c_opengl.GL_RENDERBUFFER_DEPTH_SIZE
GL_RENDERBUFFER_STENCIL_SIZE = c_opengl.GL_RENDERBUFFER_STENCIL_SIZE
GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE = c_opengl.GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE
GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME = c_opengl.GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME
GL_FRAMEBUFFER_ATTACHMENT_TEXTURE_LEVEL = c_opengl.GL_FRAMEBUFFER_ATTACHMENT_TEXTURE_LEVEL
GL_FRAMEBUFFER_ATTACHMENT_TEXTURE_CUBE_MAP_FACE = c_opengl.GL_FRAMEBUFFER_ATTACHMENT_TEXTURE_CUBE_MAP_FACE
GL_COLOR_ATTACHMENT0 = c_opengl.GL_COLOR_ATTACHMENT0
GL_DEPTH_ATTACHMENT = c_opengl.GL_DEPTH_ATTACHMENT
GL_STENCIL_ATTACHMENT = c_opengl.GL_STENCIL_ATTACHMENT
GL_NONE = c_opengl.GL_NONE
GL_FRAMEBUFFER_COMPLETE = c_opengl.GL_FRAMEBUFFER_COMPLETE
GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT = c_opengl.GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT
GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT = c_opengl.GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT
GL_FRAMEBUFFER_INCOMPLETE_DIMENSIONS = c_opengl.GL_FRAMEBUFFER_INCOMPLETE_DIMENSIONS
GL_FRAMEBUFFER_UNSUPPORTED = c_opengl.GL_FRAMEBUFFER_UNSUPPORTED
GL_FRAMEBUFFER_BINDING = c_opengl.GL_FRAMEBUFFER_BINDING
GL_RENDERBUFFER_BINDING = c_opengl.GL_RENDERBUFFER_BINDING
GL_MAX_RENDERBUFFER_SIZE = c_opengl.GL_MAX_RENDERBUFFER_SIZE
GL_INVALID_FRAMEBUFFER_OPERATION = c_opengl.GL_INVALID_FRAMEBUFFER_OPERATION


def glActiveTexture (GLenum texture):
   c_opengl.glActiveTexture (texture) 

def glAttachShader (GLuint program, GLuint shader):
   c_opengl.glAttachShader (program, shader) 

def glBindAttribLocation (GLuint program, GLuint index,  GLchar* name):
   c_opengl.glBindAttribLocation (program, index, name) 

def glBindBuffer (GLenum target, GLuint buffer):
   c_opengl.glBindBuffer (target, buffer) 

def glBindFramebuffer (GLenum target, GLuint framebuffer):
   c_opengl.glBindFramebuffer (target, framebuffer) 

def glBindRenderbuffer (GLenum target, GLuint renderbuffer):
   c_opengl.glBindRenderbuffer (target, renderbuffer) 

def glBindTexture (GLenum target, GLuint texture):
   c_opengl.glBindTexture (target, texture) 

def glBlendColor (GLclampf red, GLclampf green, GLclampf blue, GLclampf alpha):
   c_opengl.glBlendColor (red, green, blue, alpha) 

def glBlendEquation (GLenum mode ):
   c_opengl.glBlendEquation (mode ) 

def glBlendEquationSeparate (GLenum modeRGB, GLenum modeAlpha):
   c_opengl.glBlendEquationSeparate (modeRGB, modeAlpha) 

def glBlendFunc (GLenum sfactor, GLenum dfactor):
   c_opengl.glBlendFunc (sfactor, dfactor) 

def glBlendFuncSeparate (GLenum srcRGB, GLenum dstRGB, GLenum srcAlpha, GLenum dstAlpha):
   c_opengl.glBlendFuncSeparate (srcRGB, dstRGB, srcAlpha, dstAlpha) 

def glBufferData (GLenum target, GLsizeiptr size,  GLvoid* data, GLenum usage):
   c_opengl.glBufferData (target, size, data, usage) 

def glBufferSubData (GLenum target, GLintptr offset, GLsizeiptr size,  GLvoid* data):
   c_opengl.glBufferSubData (target, offset, size, data) 

def glCheckFramebufferStatus (GLenum target):
    cdef GLenum result   
    result = c_opengl.CheckFramebufferStatus (target) 
    return result

def glClear (GLbitfield mask):
   c_opengl.glClear (mask) 

def glClearColor (GLclampf red, GLclampf green, GLclampf blue, GLclampf alpha):
   c_opengl.glClearColor (red, green, blue, alpha) 

def glClearDepthf (GLclampf depth):
   c_opengl.glClearDepthf (depth) 

def glClearStencil (GLint s):
   c_opengl.glClearStencil (s) 

def glColorMask (GLboolean red, GLboolean green, GLboolean blue, GLboolean alpha):
   c_opengl.glColorMask (red, green, blue, alpha) 

def glCompileShader (GLuint shader):
   c_opengl.glCompileShader (shader) 

def glCompressedTexImage2D (GLenum target, GLint level, GLenum internalformat, GLsizei width, GLsizei height, GLint border, GLsizei imageSize,  GLvoid* data):
   c_opengl.glCompressedTexImage2D (target, level, internalformat, width, height, border, imageSize, data) 

def glCompressedTexSubImage2D (GLenum target, GLint level, GLint xoffset, GLint yoffset, GLsizei width, GLsizei height, GLenum format, GLsizei imageSize,  GLvoid* data):
   c_opengl.glCompressedTexSubImage2D (target, level, xoffset, yoffset, width, height, format, imageSize, data) 

def glCopyTexImage2D (GLenum target, GLint level, GLenum internalformat, GLint x, GLint y, GLsizei width, GLsizei height, GLint border):
   c_opengl.glCopyTexImage2D (target, level, internalformat, x, y, width, height, border) 

def glCopyTexSubImage2D (GLenum target, GLint level, GLint xoffset, GLint yoffset, GLint x, GLint y, GLsizei width, GLsizei height):
   c_opengl.glCopyTexSubImage2D (target, level, xoffset, yoffset, x, y, width, height) 

def glCreateProgram ():
   cdef GLuint id
   id = c_opengl.CreateProgram () 
   return id

def glCreateShader (GLenum type):
   cdef GLuint id
   c_opengl.glCreateShader (type) 
   return id

def glCullFace (GLenum mode):
   c_opengl.glCullFace (mode) 

def glDeleteBuffers (GLsizei n,  GLuint* buffers):
   c_opengl.glDeleteBuffers (n, buffers) 

def glDeleteFramebuffers (GLsizei n,  GLuint* framebuffers):
   c_opengl.glDeleteFramebuffers (n, framebuffers) 

def glDeleteProgram (GLuint program):
   c_opengl.glDeleteProgram (program) 

def glDeleteRenderbuffers (GLsizei n,  GLuint* renderbuffers):
   c_opengl.glDeleteRenderbuffers (n, renderbuffers) 

def glDeleteShader (GLuint shader):
   c_opengl.glDeleteShader (shader) 

def glDeleteTextures (GLsizei n,  GLuint* textures):
   c_opengl.glDeleteTextures (n, textures) 

def glDepthFunc (GLenum func):
   c_opengl.glDepthFunc (func) 

def glDepthMask (GLboolean flag):
   c_opengl.glDepthMask (flag) 

def glDepthRangef (GLclampf zNear, GLclampf zFar):
   c_opengl.glDepthRangef (zNear, zFar) 

def glDetachShader (GLuint program, GLuint shader):
   c_opengl.glDetachShader (program, shader) 

def glDisable (GLenum cap):
   c_opengl.glDisable (cap) 

def glDisableVertexAttribArray (GLuint index):
   c_opengl.glDisableVertexAttribArray (index) 

def glDrawArrays (GLenum mode, GLint first, GLsizei count):
   c_opengl.glDrawArrays (mode, first, count) 

def glDrawElements (GLenum mode, GLsizei count, GLenum type,  GLvoid* indices):
   c_opengl.glDrawElements (mode, count, type, indices) 

def glEnable (GLenum cap):
   c_opengl.glEnable (cap) 

def glEnableVertexAttribArray (GLuint index):
   c_opengl.glEnableVertexAttribArray (index) 

def glFinish ():
   c_opengl.glFinish () 

def glFlush ():
   c_opengl.glFlush () 

def glFramebufferRenderbuffer (GLenum target, GLenum attachment, GLenum renderbuffertarget, GLuint renderbuffer):
   c_opengl.glFramebufferRenderbuffer (target, attachment, renderbuffertarget, renderbuffer) 

def glFramebufferTexture2D (GLenum target, GLenum attachment, GLenum textarget, GLuint texture, GLint level):
   c_opengl.glFramebufferTexture2D (target, attachment, textarget, texture, level) 

def glFrontFace (GLenum mode):
   c_opengl.glFrontFace (mode) 

def glGenBuffers (GLsizei n, GLuint* buffers):
   c_opengl.glGenBuffers (n, buffers) 

def glGenerateMipmap (GLenum target):
   c_opengl.glGenerateMipmap (target) 

def glGenFramebuffers (GLsizei n, GLuint* framebuffers):
   c_opengl.glGenFramebuffers (n, framebuffers) 

def glGenRenderbuffers (GLsizei n, GLuint* renderbuffers):
   c_opengl.glGenRenderbuffers (n, renderbuffers) 

def glGenTextures (GLsizei n, GLuint* textures):
   c_opengl.glGenTextures (n, textures) 

def glGetActiveAttrib (GLuint program, GLuint index, GLsizei bufsize, GLsizei* length, GLint* size, GLenum* type, GLchar* name):
   c_opengl.glGetActiveAttrib (program, index, bufsize, length, size, type, name) 

def glGetActiveUniform (GLuint program, GLuint index, GLsizei bufsize, GLsizei* length, GLint* size, GLenum* type, GLchar* name):
   c_opengl.glGetActiveUniform (program, index, bufsize, length, size, type, name) 

def glGetAttachedShaders (GLuint program, GLsizei maxcount, GLsizei* count, GLuint* shaders):
   c_opengl.glGetAttachedShaders (program, maxcount, count, shaders) 

def glGetAttribLocation (GLuint program,  GLchar* name):
   cdef int location 
   location = c_opengl.glGetAttribLocation (program, name)
   return location 

def glGetBooleanv (GLenum pname, GLboolean* params):
   c_opengl.glGetBooleanv (pname, params) 

def glGetBufferParameteriv (GLenum target, GLenum pname, GLint* params):
   c_opengl.glGetBufferParameteriv (target, pname, params) 

def glGetError ():
   cdef GLenum err
   c_opengl.glGetError () 
   return err


#TODO: figure out best way to return data...will be different size based on parameter queried
"""
def glGetFloatv (GLenum pname, GLfloat* params):
   c_opengl.glGetFloatv (pname, params) 

def glGetFramebufferAttachmentParameteriv (GLenum target, GLenum attachment, GLenum pname, GLint* params):
   c_opengl.glGetFramebufferAttachmentParameteriv (target, attachment, pname, params) 

def glGetIntegerv (GLenum pname, GLint* params):
   c_opengl.glGetIntegerv (pname, params) 

def glGetProgramiv (GLuint program, GLenum pname, GLint* params):
   c_opengl.glGetProgramiv (program, pname, params) 

def glGetProgramInfoLog (GLuint program, GLsizei bufsize, GLsizei* length, GLchar* infolog):
   c_opengl.glGetProgramInfoLog (program, bufsize, length, infolog) 

def glGetRenderbufferParameteriv (GLenum target, GLenum pname, GLint* params):
   c_opengl.glGetRenderbufferParameteriv (target, pname, params) 

def glGetShaderiv (GLuint shader, GLenum pname, GLint* params):
   c_opengl.glGetShaderiv (shader, pname, params) 

def glGetShaderInfoLog (GLuint shader, GLsizei bufsize, GLsizei* length, GLchar* infolog):
   c_opengl.glGetShaderInfoLog (shader, bufsize, length, infolog) 

def glGetShaderPrecisionFormat (GLenum shadertype, GLenum precisiontype, GLint* range, GLint* precision):
   c_opengl.glGetShaderPrecisionFormat (shadertype, precisiontype, range, precision) 

def glGetShaderSource (GLuint shader, GLsizei bufsize, GLsizei* length, GLchar* source):
   c_opengl.glGetShaderSource (shader, bufsize, length, source) 

def glGetString (GLenum name):
   #return GLubyte*
   c_opengl.glGetString (name) 

def glGetTexParameterfv (GLenum target, GLenum pname, GLfloat* params):
   c_opengl.glGetTexParameterfv (target, pname, params) 

def glGetTexParameteriv (GLenum target, GLenum pname, GLint* params):
   c_opengl.glGetTexParameteriv (target, pname, params) 

def glGetUniformfv (GLuint program, GLint location, GLfloat* params):
   c_opengl.glGetUniformfv (program, location, params) 

def glGetUniformiv (GLuint program, GLint location, GLint* params):
   c_opengl.glGetUniformiv (program, location, params) 

def glGetUniformLocation (GLuint program,  GLchar* name):
   cdef int loc
   loc = c_opengl.glGetUniformLocation (program, name) 
   return loc

def glGetVertexAttribfv (GLuint index, GLenum pname, GLfloat* params):
   c_opengl.glGetVertexAttribfv (index, pname, params) 

def glGetVertexAttribiv (GLuint index, GLenum pname, GLint* params):
   c_opengl.glGetVertexAttribiv (index, pname, params) 

def glGetVertexAttribPointerv (GLuint index, GLenum pname, GLvoid** pointer):
   c_opengl.glGetVertexAttribPointerv (index, pname, pointer) 
"""



def glHint (GLenum target, GLenum mode):
   c_opengl.glHint (target, mode) 

def glIsBuffer (GLuint buffer):
    cdef GLboolean b   
    b = c_opengl.IsBuffer (buffer) 
    return b

def glIsEnabled (GLenum cap):
   cdef GLboolean b   
   c_opengl.glIsEnabled (cap) 
   return b

def glIsFramebuffer (GLuint framebuffer):
   cdef GLboolean b   
   c_opengl.glIsFramebuffer (framebuffer) 
   return b

def glIsProgram (GLuint program):
   cdef GLboolean b   
   c_opengl.glIsProgram (program) 
   return b

def glIsRenderbuffer (GLuint renderbuffer):
   cdef GLboolean b   
   c_opengl.glIsRenderbuffer (renderbuffer) 
   return b

def glIsShader (GLuint shader):
   cdef GLboolean b   
   c_opengl.glIsShader (shader) 
   return b

def glIsTexture (GLuint texture):
   cdef GLboolean b   
   c_opengl.glIsTexture (texture) 
   return b

def glLineWidth (GLfloat width):
   c_opengl.glLineWidth (width) 

def glLinkProgram (GLuint program):
   c_opengl.glLinkProgram (program) 

def glPixelStorei (GLenum pname, GLint param):
   c_opengl.glPixelStorei (pname, param) 

def glPolygonOffset (GLfloat factor, GLfloat units):
   c_opengl.glPolygonOffset (factor, units) 

def glReadPixels (GLint x, GLint y, GLsizei width, GLsizei height, GLenum format, GLenum type, GLvoid* pixels):
   c_opengl.glReadPixels (x, y, width, height, format, type, pixels) 

def glReleaseShaderCompiler ():
   c_opengl.glReleaseShaderCompiler () 

def glRenderbufferStorage (GLenum target, GLenum internalformat, GLsizei width, GLsizei height):
   c_opengl.glRenderbufferStorage (target, internalformat, width, height) 

def glSampleCoverage (GLclampf value, GLboolean invert):
   c_opengl.glSampleCoverage (value, invert) 

def glScissor (GLint x, GLint y, GLsizei width, GLsizei height):
   c_opengl.glScissor (x, y, width, height) 

def glShaderBinary (GLsizei n,  GLuint* shaders, GLenum binaryformat,  GLvoid* binary, GLsizei length):
   c_opengl.glShaderBinary (n, shaders, binaryformat, binary, length) 

def glShaderSource (GLuint shader,  str string):
   c_opengl.glShaderSource (shader, 1, string, 0) 

def glStencilFunc (GLenum func, GLint ref, GLuint mask):
   c_opengl.glStencilFunc (func, ref, mask) 

def glStencilFuncSeparate (GLenum face, GLenum func, GLint ref, GLuint mask):
   c_opengl.glStencilFuncSeparate (face, func, ref, mask) 

def glStencilMask (GLuint mask):
   c_opengl.glStencilMask (mask) 

def glStencilMaskSeparate (GLenum face, GLuint mask):
   c_opengl.glStencilMaskSeparate (face, mask) 

def glStencilOp (GLenum fail, GLenum zfail, GLenum zpass):
   c_opengl.glStencilOp (fail, zfail, zpass) 

def glStencilOpSeparate (GLenum face, GLenum fail, GLenum zfail, GLenum zpass):
   c_opengl.glStencilOpSeparate (face, fail, zfail, zpass) 

#def glTexImage2D (GLenum target, GLint level, GLint internalformat, GLsizei width, GLsizei height, GLint border, GLenum format, GLenum type,  GLvoid* pixels):
#   c_opengl.glTexImage2D (target, level, internalformat, width, height, border, format, type, pixels) 

def glTexParameterf (GLenum target, GLenum pname, GLfloat param):
   c_opengl.glTexParameterf (target, pname, param) 

#def glTexParameterfv (GLenum target, GLenum pname,  GLfloat* params):
#   c_opengl.glTexParameterfv (target, pname, params) 

def glTexParameteri (GLenum target, GLenum pname, GLint param):
   c_opengl.glTexParameteri (target, pname, param) 

#def glTexParameteriv (GLenum target, GLenum pname,  GLint* params):
#   c_opengl.glTexParameteriv (target, pname, params) 

#def glTexSubImage2D (GLenum target, GLint level, GLint xoffset, GLint yoffset, GLsizei width, GLsizei height, GLenum format, GLenum type,  GLvoid* pixels):
#   c_opengl.glTexSubImage2D (target, level, xoffset, yoffset, width, height, format, type, pixels) 

def glUniform1f (GLint location, GLfloat x):
   c_opengl.glUniform1f (location, x) 

#def glUniform1fv (GLint location, GLsizei count,  GLfloat* v):
#   c_opengl.glUniform1fv (location, count, v) 

def glUniform1i (GLint location, GLint x):
   c_opengl.glUniform1i (location, x) 

#def glUniform1iv (GLint location, GLsizei count,  GLint* v):
#   c_opengl.glUniform1iv (location, count, v) 

def glUniform2f (GLint location, GLfloat x, GLfloat y):
   c_opengl.glUniform2f (location, x, y) 

#def glUniform2fv (GLint location, GLsizei count,  GLfloat* v):
#   c_opengl.glUniform2fv (location, count, v) 

def glUniform2i (GLint location, GLint x, GLint y):
   c_opengl.glUniform2i (location, x, y) 

#def glUniform2iv (GLint location, GLsizei count,  GLint* v):
#   c_opengl.glUniform2iv (location, count, v) 

def glUniform3f (GLint location, GLfloat x, GLfloat y, GLfloat z):
   c_opengl.glUniform3f (location, x, y, z) 

#def glUniform3fv (GLint location, GLsizei count,  GLfloat* v):
#   c_opengl.glUniform3fv (location, count, v) 

def glUniform3i (GLint location, GLint x, GLint y, GLint z):
   c_opengl.glUniform3i (location, x, y, z) 

#def glUniform3iv (GLint location, GLsizei count,  GLint* v):
#   c_opengl.glUniform3iv (location, count, v) 

def glUniform4f (GLint location, GLfloat x, GLfloat y, GLfloat z, GLfloat w):
   c_opengl.glUniform4f (location, x, y, z, w) 

#def glUniform4fv (GLint location, GLsizei count,  GLfloat* v):
#   c_opengl.glUniform4fv (location, count, v) 

def glUniform4i (GLint location, GLint x, GLint y, GLint z, GLint w):
   c_opengl.glUniform4i (location, x, y, z, w) 

#def glUniform4iv (GLint location, GLsizei count,  GLint* v):
#   c_opengl.glUniform4iv (location, count, v) 

#def glUniformMatrix2fv (GLint location, GLsizei count, GLboolean transpose,  GLfloat* value):
def glUniformMatrix2fv (GLint location, GLsizei count, GLboolean transpose,  bytes values):
   cdef char* ptr_value = values
   c_opengl.glUniformMatrix2fv (location, count, transpose, <GLfloat*>ptr_value) 

#def glUniformMatrix3fv (GLint location, GLsizei count, GLboolean transpose,  GLfloat* value):
def glUniformMatrix3fv (GLint location, GLsizei count, GLboolean transpose,  bytes values):
   cdef char* ptr_value = values
   c_opengl.glUniformMatrix3fv (location, count, transpose, <GLfloat*>ptr_value) 

#def glUniformMatrix4fv (GLint location, GLsizei count, GLboolean transpose,  GLfloat* value):
def glUniformMatrix4fv (GLint location, GLsizei count, GLboolean transpose,  bytes values):
   cdef char* ptr_value = values
   c_opengl.glUniformMatrix4fv (location, count, transpose, <GLfloat*>ptr_value) 

def glUseProgram (GLuint program):
   c_opengl.glUseProgram (program) 

def glValidateProgram (GLuint program):
   c_opengl.glValidateProgram (program) 

def glVertexAttrib1f (GLuint indx, GLfloat x):
   c_opengl.glVertexAttrib1f (indx, x) 

#def glVertexAttrib1fv (GLuint indx,  GLfloat* values):
#   c_opengl.glVertexAttrib1fv (indx, values) 

def glVertexAttrib2f (GLuint indx, GLfloat x, GLfloat y):
   c_opengl.glVertexAttrib2f (indx, x, y) 

#def glVertexAttrib2fv (GLuint indx,  GLfloat* values):
#   c_opengl.glVertexAttrib2fv (indx, values) 

def glVertexAttrib3f (GLuint indx, GLfloat x, GLfloat y, GLfloat z):
   c_opengl.glVertexAttrib3f (indx, x, y, z) 

#def glVertexAttrib3fv (GLuint indx,  GLfloat* values):
#   c_opengl.glVertexAttrib3fv (indx, values) 

def glVertexAttrib4f (GLuint indx, GLfloat x, GLfloat y, GLfloat z, GLfloat w):
   c_opengl.glVertexAttrib4f (indx, x, y, z, w) 

#def glVertexAttrib4fv (GLuint indx,  GLfloat* values):
#   c_opengl.glVertexAttrib4fv (indx, values) 

#def glVertexAttribPointer (GLuint indx, GLint size, GLenum type, GLboolean normalized, GLsizei stride,  GLvoid* ptr):
def glVertexAttribPointer (GLuint indx, GLint size, GLenum type, GLboolean normalized, GLsizei stride,  int ptr):
   c_opengl.glVertexAttribPointer (indx, size, type, normalized, stride, <GLvoid*>ptr) 

def glViewport (GLint x, GLint y, GLsizei width, GLsizei height):
   c_opengl.glViewport (x, y, width, height) 

	







