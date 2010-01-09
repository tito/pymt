'''
Video widget: provide a video container
'''


__all__ = ('MTVideo', 'MTSimpleVideo')

import os
import pymt
from OpenGL.GL import *
from ...factory import MTWidgetFactory
from ..layout import MTBoxLayout
from ..button import MTImageButton
from ..slider import MTSlider
from ..widget import MTWidget

iconPath = os.path.dirname(pymt.__file__) + '/data/icons/'

class MTSimpleVideo(MTWidget):
    def __init__(self, filename, **kwargs):
        '''Provides a basic Video Widget with options on controlling the playback.
        This widget is based on the Video provider.
           * Double tap: Pause/Play
           * Two Finger Double tap: Rewind

        :Parameters:
            `autostart` : bool, default to False
                Autostart the video at instance
        '''
        kwargs.setdefault('autostart', False)

        self._touches = {}

        super(MTSimpleVideo, self).__init__(**kwargs)

        # load video
        self.player = pymt.Video(filename=filename)

        # autostart the video ?
        if kwargs.get('autostart'):
            self.player.play()

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self._touches[touch.uid] = (touch.x, touch.y)
            if len(self._touches) == 2:
                if touch.is_double_tap:
                    self.player.seek(0)
            elif touch.is_double_tap:
                if self.player.state == 'playing':
                    self.player.stop()
                else:
                    self.player.play()

        return super(MTSimpleVideo, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.uid in self._touches:
            del self._touches[touch.uid]
        return super(MTSimpleVideo, self).on_touch_up(touch)

    def on_update(self):
        self.size = self.player.size
        self.player.update()
        super(MTSimpleVideo, self).on_update()

    def draw(self):
        self.player.draw()
        super(MTSimpleVideo, self).draw()


class MTButtonVideo(MTImageButton):
    def draw(self):
        pymt.set_color(*self.style['bg-color'])
        pymt.drawCSSRectangle(pos=self.pos, size=self.size, style=self.style)
        self.image.color = self.style['color']
        super(MTButtonVideo, self).draw()

class MTVideo(MTSimpleVideo):
    '''MTVideo is a video player, with control buttons.
    You can use it like this ::

          video = MTVideo(filename='source_file')

    :Parameters:
        `filename` : str
            Filename of video
        `bordersize` : int, default to 10
            Border size of the video
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('bordersize', 10)

        super(MTVideo, self).__init__(**kwargs)

        self._count = 0
        self._controls = False
        self.bordersize = kwargs.get('bordersize')

        # images play/pause/mute
        self.f_play = pymt.Image(iconPath + 'video-play.png')
        self.f_pause = pymt.Image(iconPath + 'video-pause.png')
        self.f_vmute = pymt.Image(iconPath + 'video-volume-mute.png')
        self.f_v100 = pymt.Image(iconPath + 'video-volume-100.png')

        # create UI
        box = MTBoxLayout(orientation='horizontal', uniform_height=True,
                          spacing=0, padding=0)
        self._btnplay = MTButtonVideo(image=self.f_play,
                                      cls='video-toggleplay')
        self._btnmute = MTButtonVideo(image=self.f_v100,
                                      cls='video-togglemute')
        self._timeline = MTSlider(orientation='horizontal',
                                  cls='video-timeline')

        box.add_widget(self._btnplay)
        box.add_widget(self._btnmute)
        box.add_widget(self._timeline)
        self.add_widget(box)

        # link
        self._btnplay.connect('on_press', self._on_toggle_play)
        self._btnmute.connect('on_press', self._on_toggle_mute)

        self.hide_controls()

    def _on_toggle_play(self, *largs):
        if self.player.state == 'playing':
            self.player.stop()
            self._btnplay.image = self.f_pause
        else:
            self.player.play()
            self._btnplay.image = self.f_play
        return True

    def _on_toggle_mute(self, *largs):
        if self.player.volume == 1:
            self.player.volume = 0
            self._btnmute.image = self.f_vmute
        else:
            self.player.volume = 1
            self._btnmute.image = self.f_v100
        return True

    def on_update(self):
        super(MTVideo, self).on_update()
        # don't update controls if nothing is showed
        if self._controls == False:
            return
        self._timeline.width = self.width - self._btnplay.width - self._btnmute.width
        self._timeline.max = self.player.duration
        self._timeline.value = self.player.position

    def on_resize(self, w, h):
        self._timeline.width = w - 60
        return super(MTVideo, self).on_resize(w, h)

    def draw(self):
        b = self.bordersize
        b2 = b * 2
        pymt.set_color(*self.style['bg-color'])
        pymt.drawCSSRectangle((-b, -b), (self.width + b2, self.height + b2),
                              style=self.style)
        super(MTVideo, self).draw()

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.show_controls()
            self._count += 1
            pymt.getClock().schedule_once(self._try_hide_controls, 5)
        return super(MTVideo, self).on_touch_down(touch)

    def _try_hide_controls(self, *largs):
        self._count -= 1
        if self._count == 0:
            self.hide_controls()

    def show_controls(self):
        '''Makes the video controls visible'''
        self._controls = True
        for w in self.children:
            w.show()

    def hide_controls(self):
        '''Hides the video controls'''
        self._controls = False
        for w in self.children:
            w.hide()


# Register all base widgets
MTWidgetFactory.register('MTVideo', MTVideo)
MTWidgetFactory.register('MTSimpleVideo', MTSimpleVideo)
