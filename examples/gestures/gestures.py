from pymt import *

import pickle, base64, zlib
from cStringIO import StringIO

class GestureDatabase(object):
    def __init__(self):
        self.db = []

    def add_gesture(self, gesture):
        self.db.append(gesture)

    def find(self, gesture, minscore=0.9):
        best = None
        bestscore = minscore
        for g in self.db:
            score = g.get_score(gesture)
            if score < bestscore:
                continue
            bestscore = score
            best = g
        if not best:
            return
        return (bestscore, best)

    def gesture_to_str(self, gesture):
        io = StringIO()
        p = pickle.Pickler(io)
        p.dump(gesture)
        data = base64.b64encode(zlib.compress(io.getvalue(), 9))
        return data

    def str_to_gesture(self, data):
        io = StringIO(zlib.decompress(base64.b64decode(data)))
        p = pickle.Unpickler(io)
        gesture = p.load()
        return gesture


class MTGestureWidget(MTWidget):
    def __init__(self, gdb):
        super(MTGestureWidget, self).__init__()
        self.gdb = gdb
        self.points = {}
        self.db = []

    def on_touch_down(self, touches, touchID, x, y):
        if not self.points.has_key(touchID):
            self.points[touchID] = []
        self.points[touchID].append((x, y))

    def on_touch_move(self, touches, touchID, x, y):
        if not self.points.has_key(touchID):
            return
        self.points[touchID].append((x, y))

    def on_touch_up(self, touches, touchID, x, y):
        if not self.points.has_key(touchID):
            return
        self.points[touchID].append((x, y))

        # create Gesture from stroke
        g = Gesture()
        g.add_stroke(self.points[touchID])
        g.normalize()

        # try to find gesture from database
        best = self.gdb.find(g, minscore=0.8)
        if not best:
            print 'No gesture found'
        else:
            print 'Gesture found, score', best[0], ':', best[1].label

        # activate this to have string representation
        #print 'Representation of this gesture', self.gdb.gesture_to_str(g)

        # reset stroke
        del self.points[touchID]


if __name__ == '__main__':
    gdb = GestureDatabase()

    # Circle
    g = gdb.str_to_gesture('eNqFkMtqw0AMRff6EXtTo8doHj+Qbgv+gJImJoSm8eCZQPP3HTlpodDHIJiFdO7VVX/M17c6HKZSL8sEj/c/I/T7TDB2pS7z61Q6yAz9KQv0PxLjOgbZGaeNy/PxXA3zhoVfsCebghyNSo26NoAQNjhwiI45iiJ7j5EVyti9W5usTc6JkGpyrDElTVBetn96EK+RBA43AyHvveNEgYJScgHK4aaNilG5GWBAkabu/xdfc5N+iScvLogX4eiS4qf4Q9uclJAdtmwtFbEzcauxq/NpWrbn3WQx/RoTvz+yK9xXeM7LvL/sqg2H1TS0g7RAjiOLqNhNhg+4A4YT')
    g.label = 'Circle'
    gdb.add_gesture(g)

    # Up
    g = gdb.str_to_gesture('eNqdkE1qAzEMhfe6yMwmRvK/L5BuC3OAkiZmCE0zZuxAcvtYHndRaLuoMc9gv+9J8nhOj88i5pjLbY3w0s+EMJ4SwTTksi4fMQ+QJIyXpGD8kZiaDZJmzlQuLedrYcwy5n7BXtkFyTMVKvWoACHsdyhMCM5SQN3UKA95Gu78TrBHgVL3J1bvnYL8fvizCsk2lIL5q4T15K3yyigpScsAef5/ehudzJaOQiNK5TGYptrKHr7j9H676RbOexrKconr4XqMPKjlHMLvi/gfegtvaV1Ot2Nhs2Oz17VfbhfR1Whta7J4AhYuhrk=')
    g.label = 'Up'
    gdb.add_gesture(g)

    # NUI-wave
    g = gdb.str_to_gesture('eNqFkMtuwyAQRffzI/am1jwYBn6g3VbyB1RpYkVR0xjZRGr+vkCdRaU+EBIL7jmXoT+l23sejtOar8sET9uZEPpDIhi7NS/z27R2kBj6cxLofyTGFoPkKqeFS/PpkivmK2a/YM81BSlUKhbqVgBCeHzAAX2g4KOLXhFFAhKsY/dRA9QCyjFECYFYjGN05f5192cNcZtK4HjvEBMrEmRE51jYYD3e9eiUWY0IWRxZ+F/fhif90uNApCoSA2pgZcdxk+PgDAk9UTDPVqqbu+6xy/N5WnaX/VQH9U2D31f7h+0FL2mZD9d9rmGrYTM11tpIJuX1rpiHT145hrs=')
    g.label = 'NUI-wave'
    gdb.add_gesture(g)

    w = MTWindow()
    w.add_widget(MTGestureWidget(gdb))
    runTouchApp()
