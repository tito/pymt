'''
Exception Manager: add/remove handler for exception in application
'''

__all__ = ('pymt_exception_manager', 'ExceptionHandler', 'ExceptionManager')

class ExceptionHandler:
    '''Base handler that catch exception in runTouchApp().
    You can derivate and use it like this ::

        class E(ExceptionHandler):
            def handle_exception(self, inst):
                pymt_logger.exception(inst)
                return ExceptionManager.PASS

        pymt_exception_manager.add_handler(E())

    All exceptions will be set to PASS, and loggued to console !
    '''
    def __init__(self):
        pass

    def handle_exception(self, exception):
        '''Handle one exception, default return ExceptionManager.STOP'''
        return ExceptionManager.RAISE

class ExceptionManager:
    '''ExceptionManager manage exceptions handlers.'''

    RAISE   = 0
    PASS    = 1

    def __init__(self):
        self.handlers = []
        self.policy = ExceptionManager.RAISE

    def add_handler(self, cls):
        '''Add a new exception handler in the stack'''
        if not cls in self.handlers:
            self.handlers.append(cls)

    def remove_handler(self, cls):
        '''Remove a exception handler from the stack'''
        if cls in self.handlers:
            self.handlers.remove(cls)

    def handle_exception(self, inst):
        '''Called when an exception happend in runTouchApp() main loop'''
        ret = self.policy
        for handler in self.handlers:
            r = handler.handle_exception(inst)
            if r == ExceptionManager.PASS:
                ret = r
        return ret

#: PyMT Exception Manager instance
pymt_exception_manager = ExceptionManager()
