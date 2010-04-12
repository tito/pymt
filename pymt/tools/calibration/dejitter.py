from pymt import *


class JitterSensor(MTWidget):
    """Explanation:
    This widget helps you to find a good jitter_distance setting for your
    specific multi-touch setup. Just follow the instructions. The amount of
    your BLOB's jitter will be measured and a fitting configuration value will be
    set in your configuration file.
    """
    def __init__(self, **kwargs):
        super(JitterSensor, self).__init__(**kwargs)
        self.margin = 5
        # The touch we want to observe
        self.touch = None
        # Here we note down all of the touches positions
        self.touchs_spositions = []
        # We need to give the user a second to get his finger into a still pos.
        # Indicate whether we're ready. We will just start with a short delay.
        self._ready = False
        # Indicate whether we finished calibration. Don't take any more touches
        # into account when done.
        self._done = False
        # When the touch is stable, get the original position
        self.original_spos = None
        self.switch_label()
        # Being lazy here. Just reuse the docstring :-)
        explanation = MTLabel(pos=(10, 10), anchor_x='left', anchor_y='top',
                              autosize=True, label=self.__doc__)
        self.add_widget(explanation)

    def switch_label(self):
        try:
            self.remove_widget(self.label)
        except AttributeError:
            # No label yet, no problem.
            pass
        if not self._ready:
            label = 'Hold down ONE finger in the red\n' + \
                    'rectangle and do not move or lift it.'
        if self.touch is not None and not self._ready:
            label = 'Now hold that finger still!'
        if self._done:
            label = 'You may now lift your finger.'
        x, y = self.pos
        self.label = MTLabel(pos=(x+self.width+5, y+self.height/2), label=label)
        self.add_widget(self.label)

    def ready(self, dt):
        # Timeout passed. We're ready!
        self._ready = True
        self.original_spos = self.touch.spos
        getClock().schedule_once(self.done, 15)

    def done(self, dt):
        self._done = True
        self.switch_label()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.touch = touch
            # Wait two seconds before measuring
            getClock().schedule_once(self.ready, 0.5)
            self.switch_label()

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos) and touch is self.touch and self._ready:
            if self._done:
                return
            self.touchs_spositions.append(touch.spos)

    def on_touch_up(self, touch):
        if touch is self.touch:
            getClock().unschedule(self.ready)
            getClock().unschedule(self.done)
            maxmean = self.calculate_derivation()
            if maxmean:
                pymt_config.set('pymt', 'jitter_distance', maxmean)
                pymt_config.write()
                content = ('%f is a good jitter_distance value for you. It was '
                           'changed in your config file for you.') % (maxmean,)
            else:
                content = 'You got no BLOB jitter at all! Lucky you. :-)'
            if self._done:
                popup = MTModalPopup(title='Calibration Result',
                                     content=content, size=(200, 200))
                w.add_widget(popup)
            self.touch = None
            self.touchs_spositions = []
            self._ready = False
            self._done = False
            self.switch_label()

    def taxicab_distance(self, p, q):
        # Get the taxicab/manhattan/citiblock distance for efficiency reasons
        return abs(p[0]-q[0]) + abs(p[1]-q[1])

    def calculate_derivation(self):
        distances = []
        for spos in self.touchs_spositions:
            dist = self.taxicab_distance(self.original_spos, spos)
            distances.append(dist)
        # Get the x largest values and take the mean from those
        distances.sort()
        max_vals = distances[-4:]
        if not max_vals:
            # There has been no jitter at all! Prevent ZeroDivisionError
            maxmean = 0
        else:
            maxmean = sum(max_vals) / len(max_vals)
        return maxmean

    def draw(self):
        if self._done:
            set_color(0, 0, 0.8)
        elif self._ready:
            set_color(0, 0.8, 0)
        else:
            set_color(0.8, 0, 0)
        drawRectangle(self.pos, self.size)
        set_color(1, 1, 1)
        drawRectangle((self.x+self.margin, self.y+self.margin),
                      (self.width - 2 * self.margin, self.height - 2 * self.margin))


if __name__ == '__main__':
    size = (200, ) * 2
    w = getWindow()
    x = (w.width - size[0])/2
    y = (w.height - size[1])/2
    runTouchApp(JitterSensor(pos=(x,y), size=size))
