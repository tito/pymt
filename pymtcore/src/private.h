#ifndef __PYMTCORE_PRIVATE
#define __PYMTCORE_PRIVATE

#include <GL/glu.h>

#define GL(x) do {	\
	int err; (x);	\
	err = glGetError();				\
	while ( err != GL_NO_ERROR )	\
	{								\
		std::cout << #x << "(): " << gluErrorString(err) << " at " <<	\
			__FILE__ << ":" << __LINE__ << std::endl;					\
		err = glGetError();			\
	}								\
} while (0)

#define P(x) do {	\
	std::cout << #x << ": " << x << std::endl;	\
} while(0);

#define is_pow2(x) (((x) & ((x) - 1)) == 0)

#endif
