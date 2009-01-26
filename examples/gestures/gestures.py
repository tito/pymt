from pymt import *

class CaptureGesture(MTGestureWidget):
    def __init__(self, gdb):
        super(CaptureGesture, self).__init__()
        self.gdb = gdb

    def on_gesture(self, gesture, x, y):
        # try to find gesture from database
        best = self.gdb.find(gesture, minscore=0.8)
        if not best:
            print 'No gesture found\nString version of your last gesture :\n', self.gdb.gesture_to_str(best)
        else:
            print 'Gesture found, score', best[0], ':', best[1].label

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

    #A (without cross-bar)
    g = gdb.str_to_gesture('eNqFkE1qw0AMhfe6iL2pkUbS/Fwg2RZ8gJImJoSm8eCZQHP7jkxSKPRnEMxC73vSU3/Kt/c6HKdSr8sE2/ufEfpDJhi7Upf5bSodZAf9OTP0PxLjKoMsxmnj8ny6VMO8YeEX7NlUkKNRqVG3BhDC5gkH9uwcxSiSokTEBGXsPqxPa1+FXGBO3qnXFIOH8rr7cwq5NRTD8TECMRCpFyZJiSOU48OcoorjgIGVmVD/N1+Tk36Zq8eQsK2o6h3b+qs5DqIxOO+Rg7AgOTFvq7Gr83ladpf9ZDG9iQm/P7Ir3Dd4yct8uO6riQNsqOVJxF5iy0Ka7CDDJ/cphc4=')
    g.label = 'A (no cross-bar)'
    gdb.add_gesture(g)

    w = MTWindow()
    w.add_widget(CaptureGesture(gdb))
    runTouchApp()
