'''
Create/fill an heatmap in database (need PIL + sqlite3)
'''

from pymt import MTWidget, pymt_logger, pymt_config, stopTouchApp
from math import sqrt
import sys

try:
    from PIL import Image
except:
    pymt_logger.error('HeatMap: PIL package is needed to use HeatMap !')
    raise

try:
    import sqlite3
except:
    pymt_logger.error('HeatMap: sqlite3 package is needed to use HeatMap !')
    raise

class HeatMap(MTWidget):

    def __init__(self, **kwargs):
        super(HeatMap, self).__init__(**kwargs)
        self.usage()
        self.appname = sys.argv[0]
        if self.appname == '':
            self.appname = 'python'
        elif self.appname[-3:] == '.py':
            self.appname = self.appname[:-3]
        self.filename = 'heatmap-%s.db' % self.appname
        self.db = sqlite3.connect(self.filename)
        try:
            self.db.execute('''
                CREATE TABLE heatmap (
                    x NUMERIC,
                    y NUMERIC,
                    time NUMERIC
                )
            ''')
            self.db.commit()
            pymt_logger.info('HeatMap: create new database in %s' % self.filename)
        except sqlite3.OperationalError:
            pymt_logger.info('HeatMap: fill database in %s' % self.filename)

    def usage(self):
        pymt_logger.info('==================================================')
        pymt_logger.info('HeatMap module loaded.                            ')
        pymt_logger.info('                                                  ')
        pymt_logger.info('To generate the image heatmap, re-run app with :  ')
        pymt_logger.info(' -m heatmap=<options>                             ')
        pymt_logger.info('                                                  ')
        pymt_logger.info('Options availables :                              ')
        pymt_logger.info('  blend=[0-100]       % of blending between colors')
        pymt_logger.info('  dot=<integer>       Size of a click             ')
        pymt_logger.info('  filename=<str>      Output filename             ')
        pymt_logger.info('==================================================')

    def on_touch_down(self, touch):
        self.db.execute('''
            INSERT INTO heatmap
            VALUES (%f, %f, %f)
        ''' % (touch.sx, touch.sy, touch.time_start))
        self.db.commit()

    def on_update(self):
        self.bring_to_front()

    def iterate(self):
        c = self.db.cursor()
        c.execute('SELECT x, y FROM heatmap')
        for row in c:
            yield row

    def dump(self, args):
        w       = self.get_parent_window()
        dot     = 20
        blend   = 0.1
        filename = 'output.png'

        for arg in args.split(','):
            values = arg.split('=', 1)
            if len(values) == 1:
                continue
            else:
                k, v = values
                if k == 'dot':
                    dot = int(v)
                elif k == 'blend':
                    blend = float(int(v) / 100.)
                elif k == 'filename':
                    filename = v

        # show config
        pymt_logger.info('HeatMap: config dot=%d' % (dot))
        pymt_logger.info('HeatMap: config blend=%d%%' % (blend * 100.))
        pymt_logger.info('HeatMap: config filename=%s' % filename)

        # first, calculate clicks
        pymt_logger.info('HeatMap: calculate pixels map...')
        data = [0.] * w.width * w.height
        for x, y in self.iterate():
            x = int(x * w.width)
            y = int(y * w.height)
            for ix in xrange(-dot, dot):
                sx = x + ix
                if sx < 0 or sx > w.width - 1:
                    continue
                for iy in xrange(-dot, dot):
                    sy = y + iy
                    if sy < 0 or sy > w.height - 1:
                        continue
                    if ix == 0 and iy == 0:
                        a = 1
                    else:
                        a = max(0, 1 - sqrt(ix ** 2 + iy ** 2) / dot)
                    p = sy * w.width + sx
                    data[p] = data[p] + a

        pymt_logger.info('HeatMap: search maximum value in map...')
        maxvalue = 0
        for value in data:
            if value > maxvalue:
                maxvalue = value
        pymt_logger.info('HeatMap: found maximum value: %f' % maxvalue)

        # boundary of blending color
        c = 0xffffff / 3.
        s = c * .1
        s1 = float(c - s)
        s2 = float(c + s)
        s3 = float(c + c - s)
        s4 = float(c + c + s)
        s5 = float(0xffffff)

        pymt_logger.info('HeatMap: render pixels image...')
        img = Image.new('RGB', w.size, 'black')
        ppx = img.im.putpixel
        for x in xrange(w.width):
            for y in xrange(w.height):
                a = data[y * w.width + x] / float(maxvalue)
                v = int(0xffffff * a)
                if v == 0:
                    continue

                if v < s1:
                    b = v / s1
                elif v >= s1 and v < s2:
                    b = 1 - ((v - s1) / (s2 - s1))
                else:
                    b = 0

                if v >= s1 and v < s3:
                    g = ((v - s1) / (s3 - s1))
                elif v >= s3 and v < s4:
                    g = 1 - ((v - s3) / (s4 - s3))
                else:
                    g = 0

                if v >= s3:
                    r = ((v - s3) / (s5 - s3))
                else:
                    r = 0

                ppx((x, y), (int(r * 255.), int(g * 255.), int(b * 255.)))
        img.save(filename, 'PNG')

        pymt_logger.info('HeatMap: finished !')

def start(win, ctx):
    ctx.w = HeatMap()
    win.add_widget(ctx.w)

    # dump mode ?
    args = pymt_config.get('modules', 'heatmap')
    if args != '':
        ctx.w.dump(args)
        sys.exit(0)

def stop(win, ctx):
    win.remove_widget(ctx.w)
