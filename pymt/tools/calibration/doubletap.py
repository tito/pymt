#!/usr/bin/env python

from pymt import *


class DoubleTapIndicator(MTWidget):
    def __init__(self, **kwargs):
        self.red = True
        w = getWindow()
        self.diameter = max(min(*w.size)/8., 20)
        kwargs["size"] = (self.diameter, ) * 2
        super(DoubleTapIndicator, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        if touch.is_double_tap and self.collide_point(*touch.pos):
            self.red = not self.red

    def draw(self):
        if self.red:
            set_color(1, 0, 0)
        else:
            set_color(0, 0, 1)
        drawRectangle(self.pos, self.size)


class DoubleTapSettingsAdjuster(MTWidget):
    """Explanation:
    This tool can be used to adjust the doubletap settings to your liking.
    The distance that the second touch (for a doubletap) might travel (before
    both touches are considered as no doubletap) can be adjusted.
    Additionally, you can adjust the maximum time that might pass between two
    touches that you want to be considered a doubletap.
    """
    def __init__(self, **kwargs):
        super(DoubleTapSettingsAdjuster, self).__init__(**kwargs)
        self.module = m = pymt_postproc_modules["doubletap"]
        self.orig_distance = m.double_tap_distance
        self.orig_time = m.double_tap_time
        self.distance_slider = MTSlider(min=0, max=1000, value=self.orig_distance * 1000,
                                        value_show=True, orientation="horizontal")
        self.time_slider = MTSlider(min=0, max=2000, value=self.orig_time * 1000,
                                    value_show=True, orientation="horizontal")
        self.distance_slider.connect("on_value_change", self.distance_callback)
        self.time_slider.connect("on_value_change", self.time_callback)
        distlabel = MTLabel(anchor_x='left', anchor_y='bottom',
                            autosize=True, label="Maximum Distance:")
        timelabel = MTLabel(anchor_x='left', anchor_y='bottom',
                            autosize=True, label="Maximum Time:")
        touchlabel = MTLabel(anchor_x='center', anchor_y='center',
                             autosize=True, label="Test settings:")
        explanation = MTLabel(pos=(10, 10), anchor_x='left', anchor_y='top',
                              autosize=True, label=self.__doc__)
        dti = DoubleTapIndicator()
        save = MTButton(label="Save current settings", autoheight=True)
        save.connect("on_release", self.save_settings)
        reset = MTButton(label="Reset to original settings", autoheight=True)
        reset.connect("on_release", self.reset_settings)
        save.width = reset.width = dti.width = self.distance_slider.width

        self.box = MTBoxLayout(orientation="vertical", spacing=20)
        self.box.add_widget(touchlabel)
        self.box.add_widget(dti)
        self.box.add_widget(distlabel)
        self.box.add_widget(self.distance_slider)
        self.box.add_widget(timelabel)
        self.box.add_widget(self.time_slider)
        self.box.add_widget(save)
        self.box.add_widget(reset)
        w = getWindow()
        x, y = w.center
        x -= self.box.width / 2
        y -= self.box.height / 2
        self.box.pos = (x, y)
        self.add_widget(self.box)
        self.add_widget(explanation)

    def distance_callback(self, v):
        self.module.double_tap_distance = v / 1000.0
        self.module.touches = {}

    def time_callback(self, v):
        self.module.double_tap_time = v / 1000.0
        self.module.touches = {}

    def set_values(self, time, dist):
        pymt_config.set('pymt', 'double_tap_time', int(time * 1000))
        pymt_config.set('pymt', 'double_tap_distance', int(dist * 1000))
        pymt_config.write()

    def save_settings(self, touch):
        self.set_values(self.module.double_tap_time, self.module.double_tap_distance)

    def reset_settings(self, touch):
        self.set_values(self.orig_time, self.orig_distance)


if __name__ == "__main__":
    dtsa = DoubleTapSettingsAdjuster()
    runTouchApp(dtsa)
