#ifndef __PYMTCORE_COREWINDOW
#define __PYTMCORE_COREWINDOW

#include <SDL/SDL.h>
#include <GL/gl.h>
#include "private.h"

static bool is_sdl_init = false;

class CoreWindow : public CoreWidget
{
public:
	CoreWindow(): CoreWidget()
	{
		this->screen			= NULL;
		this->simulator			= NULL;

		this->do_clear			= true;
		this->fullscreen		= false;
		this->vsync				= false;
		this->display			= -1;
		this->bpp				= 32;

		if ( is_sdl_init == false )
			this->init_sdl();
	}

	virtual ~CoreWindow()
	{
	}

	bool setup(void)
	{
		int flags = SDL_HWSURFACE | SDL_OPENGL;
		if ( this->fullscreen == true )
			flags |= SDL_FULLSCREEN;

		SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1);
		SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE, 16);
		if ( this->vsync == true )
			SDL_GL_SetAttribute(SDL_GL_SWAP_CONTROL, 1);
		if ( this->display != -1 )
		{
			static char tmp[256];
			snprintf(tmp, sizeof(tmp), "SDL_VIDEO_FULLSCREEN_HEAD=%d", this->display);
			SDL_putenv(tmp);
		}

		screen = SDL_SetVideoMode((int)this->_get_width(), (int)this->_get_height(), this->bpp, flags);
		if ( screen == NULL )
		{
			// TODO add exception
			std::cout << "ERROR: unable to get OpenGL mode: " << SDL_GetError() << std::endl;
			return false;
		}

		this->__dispatch_event_dd("on_resize", this->_get_width(), this->_get_height());

		return true;
	}


	//
	// Transformation
	//

    virtual pos2d to_widget(double x, double y)
    {
		pos2d p = { x, y };
		return p;
    }

    virtual pos2d to_window(double x, double y, bool initial=false)
    {
		pos2d p = { x, y };
		return p;
    }

	virtual CoreWidget *get_root_window(void)
	{
		return this;
	}

	virtual CoreWidget *get_parent_window(void)
	{
		return this;
	}

	virtual CoreWidget *get_parent_layout(void)
	{
		return NULL;
	}


	//
	// Events
	//

	virtual bool on_close(PyObject *data)
	{
		return true;
	}

	virtual bool on_resize(PyObject *data)
	{
		double width = this->_get_width(),
			   height = this->_get_height();

		// don't dispatch on_resize, if no screen is created.
		if ( this->screen == NULL )
			return false;

		GL( glViewport(0, 0, (int)width, (int)height) );
		GL( glMatrixMode(GL_PROJECTION) );
		GL( glLoadIdentity() );
		GL( glFrustum(-width / 2, width / 2, height / 2, -height / 2, 0.1, 1000.) );
		GL( glScalef(5000., 5000., 1) );
		GL( glTranslatef((GLfloat)(-width / 2.), (GLfloat)(-height / 2.), -500) );
		GL( glMatrixMode(GL_MODELVIEW) );
		GL( glLoadIdentity() );

		return CoreWidget::on_resize(data);
	}

	virtual bool on_draw(PyObject *data)
	{
		static int fps_timer = 0;
		static int fps_frame = 0;
		static int t;

		if ( this->do_clear == true )
		{
			glClearColor(0, 0, 0, 0);
			glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
		}

		CoreWidget::on_draw(data);

		SDL_GL_SwapBuffers();
		fps_frame++;

		// update fps calculation
		t = SDL_GetTicks();
		if ( t - fps_timer >= 1000 )
		{
			double seconds = (t - fps_timer) / 1000.0;
			this->fps = fps_frame / seconds;
			std::cout << fps_frame << " frames in " << seconds
				<< " seconds = " << this->fps << " FPS" << std::endl;
			this->fps_frame = fps_frame;
			fps_frame = 0;
			fps_timer = t;
		}

		return true;
	}

	virtual bool on_update(PyObject *data)
	{
		static SDL_Event event;
		static char tmp[2];
		tmp[1] = '\0';

		while ( SDL_PollEvent(&event) )
		{
			switch ( event.type )
			{
				case SDL_MOUSEBUTTONDOWN:
					this->on_mouse_press(event.button.x, event.button.y,
							event.button.button, event.button.which);
					continue;

				case SDL_MOUSEBUTTONUP:
					this->on_mouse_release(event.button.x, event.button.y,
							event.button.button, event.button.which);
					continue;

				case SDL_MOUSEMOTION:
					this->on_mouse_drag(event.motion.x, event.motion.y,
							event.motion.xrel, event.motion.yrel,
							event.motion.state, 0);
					continue;

				case SDL_KEYDOWN:
					this->on_key_press(event.key.keysym.sym, event.key.keysym.mod);
						
					if ( (event.key.keysym.unicode & 0xFF80) == 0 ) {
						tmp[0] = (char)(event.key.keysym.unicode & 0x7F);
					}
					else
					{
						std::cout << "WARNING: an international character is pressed, ignore." << std::endl;
						continue;
					}

					this->on_text(tmp);
					continue;

				default:
					std::cout << "WARNING: received unhandled event:" << (int)event.type << std::endl;
					continue;
			}
		}

		return true;
	}


	//
	// Event dispatching
	//
	
	virtual bool dispatch_event_internal(const std::string &event_name, PyObject *data)
	{
		if ( event_name == "on_close" )
			return this->on_close(data);
		return CoreWidget::dispatch_event_internal(event_name, data);
	}


	//
	// New event for mouse and keyboard dispatching
	//

	virtual void on_mouse_press(unsigned int x, unsigned int y, int button, int modifiers)
	{
		if ( this->simulator == NULL )
			return;
	}

	virtual void on_mouse_drag(unsigned int x, unsigned int y, int dx, int dy, int button, int modifiers)
	{
		if ( this->simulator == NULL )
			return;
	}

	virtual void on_mouse_release(unsigned int x, unsigned int y, int button, int modifiers)
	{
		if ( this->simulator == NULL )
			return;
	}

	virtual void on_key_press(unsigned int symbol, unsigned int modifiers)
	{
	}

	virtual void on_text(std::string str)
	{
	}

	
	//
	// Dump informations
	//

	void dump_video_info(void)
	{
		const SDL_VideoInfo *info = SDL_GetVideoInfo();

		std::cout << "----- SDL Video mode information ------------------------" << std::endl;
		if ( info == NULL )
		{
			std::cout << "ERROR: unable to get video information" << std::endl;
			return;
		}

		std::cout << "hardware surface acceleration: " << info->hw_available << std::endl;
		std::cout << "window manager available: " << info->wm_available << std::endl;
		std::cout << "hw to hw blit: " << info->blit_hw << std::endl;
		std::cout << "hw to hw colorkey blit: " << info->blit_hw_CC << std::endl;
		std::cout << "hw to hw alpha blit: " << info->blit_hw_A << std::endl;
		std::cout << "sw to hw blit: " << info->blit_sw << std::endl;
		std::cout << "sw to hw colorkey blit: " << info->blit_sw_CC << std::endl;
		std::cout << "sw to hw alpha blit: " << info->blit_sw_A << std::endl;
		std::cout << "color fill accelerated: " << info->blit_fill << std::endl;
		std::cout << "video memory: " << info->video_mem << std::endl;
		std::cout << "current size: " << info->current_w << "x" << info->current_h << std::endl;

		std::cout << "----- SDL Pixel format ----------------------------------" << std::endl;
		if ( info->vfmt == NULL )
		{
			std::cout << "ERROR: unable to get pixel format information" << std::endl;
			return;
		}

		std::cout << "bit per pixels: " << (int)info->vfmt->BitsPerPixel << std::endl;
		std::cout << "bytes per pixels: " << (int)info->vfmt->BitsPerPixel << std::endl;
	}

	void dump_list_modes(void)
	{
		SDL_Rect** modes;
		int i;

		std::cout << "----- SDL Available video modes -------------------------" << std::endl;
		modes = SDL_ListModes(NULL, SDL_FULLSCREEN|SDL_HWSURFACE);
		if (modes == (SDL_Rect**)0)
		{
			std::cout << "ERROR: No modes available" << std::endl;
			return;
		}

		if (modes == (SDL_Rect**)-1)
		{
			std::cout << "All resolutions available." << std::endl;
			return;
		}
		else
		{
			for ( i = 0; modes[i]; ++i)
				std::cout << i << ": " << modes[i]->w << " x " << modes[i]->h << std::endl;
		}
	}


	//
	// Public Properties
	//

	bool	do_clear;
	bool	fullscreen;
	bool	vsync;
	int		display;
	int		bpp;
	int		fps_frame;
	double	fps;

protected:
	void init_sdl(void)
	{
		if ( SDL_Init(SDL_INIT_VIDEO) < 0 )
		{
			// TODO launch exception
			return;
		}
		is_sdl_init = true;
	}

private:
	PyObject	*simulator;
	SDL_Surface *screen;
};

#endif
