#ifndef __PYMTCORE_COREWINDOW
#define __PYTMCORE_COREWINDOW

#include <SDL/SDL.h>

static bool is_sdl_init = false;

class MTCoreWindow : public MTCoreWidget
{
public:
	MTCoreWindow(): MTCoreWidget()
	{
		this->screen = NULL;

		if ( is_sdl_init == false )
			this->init_sdl();
	}

	virtual ~MTCoreWindow()
	{
	}

	bool setup(int width, int height, bool fullscreen)
	{
		int flags = SDL_HWSURFACE | SDL_OPENGL;
		if ( fullscreen == true )
			flags |= SDL_FULLSCREEN;

		SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1);
		SDL_GL_SetAttribute( SDL_GL_DEPTH_SIZE, 16);

		screen = SDL_SetVideoMode(width, height, 32, flags);
		if ( screen == NULL )
		{
			// TODO add exception
			std::cout << "ERROR: unable to get OpenGL mode: " << SDL_GetError() << std::endl;
			return false;
		}

		return true;
	}

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
	SDL_Surface *screen;
};

#endif
