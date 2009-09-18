#ifndef __PYMTCORE_COREWINDOW
#define __PYTMCORE_COREWINDOW

#include <SDL/SDL.h>
#include <GL/gl.h>

static bool is_sdl_init = false;

class MTCoreWindow : public MTCoreWidget
{
public:
	MTCoreWindow(): MTCoreWidget()
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

	virtual ~MTCoreWindow()
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

		return true;
	}


	//
	// Transformation
	//

    virtual void to_widget(double x, double y, double *ox, double *oy)
    {
        *ox = x;
        *oy = y;
    }

    virtual void to_window(double x, double y, double *ox, double *oy)
    {
        *ox = x;
        *oy = y;
    }

	virtual MTCoreWidget *get_root_window(void)
	{
		return this;
	}

	virtual MTCoreWidget *get_parent_window(void)
	{
		return this;
	}

	virtual MTCoreWidget *get_parent_layout(void)
	{
		return NULL;
	}


	//
	// Events
	//

	virtual void on_resize(double width, double height)
	{
		// don't dispatch on_resize, if no screen is created.
		if ( this->screen == NULL )
			return;

		glViewport(0, 0, (int)width, (int)height);
		glMatrixMode(GL_PROJECTION);
		glLoadIdentity();
		glFrustum(-width / 2, width / 2, -height / 2, height / 2, 0.1, 1000.);
		glScalef(5000., 5000., 1);
		glTranslatef(-width / 2, -height / 2, -500);
		glMatrixMode(GL_MODELVIEW);

		MTCoreWidget::on_resize(width, height);
	}

	virtual void on_draw(void)
	{
		if ( this->do_clear == true )
			glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

		MTCoreWidget::on_draw();

		SDL_Flip(this->screen);
	}

	virtual void on_update(void)
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
						tmp[0] = event.key.keysym.unicode & 0x7F;
					}
					else
					{
						std::cout << "WARNING: an international character is pressed, ignore." << std::endl;
						continue;
					}

					this->on_text(tmp);
					continue;

				default:
					std::cout << "WARNING: received unhandled event:" << event.type << std::endl;
					continue;
			}
		}
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
