# Simple exemple of exception handler
# Exeption will be catch, and set the return to PASS
# So, app will be not stopped by this.

from pymt import *

class E(ExceptionHandler):
    def handle_exception(self, inst):
        pymt_logger.exception(inst)
        return ExceptionManager.PASS

pymt_exception_manager.add_handler(E())

m = MTWindow()
t = MTButton()
@t.event
def on_press(*largs):
    print a
m.add_widget(t)
runTouchApp()
