==============================
Handling exceptions at runtime
==============================

PyMT allow to to manage exception at runtime. You can decide what to do when an exception happen in the :keyword:`runTouchApp()` loop.

Other exception (before running application) are not catched by this manager/handler.

The manager
-----------

:keyword:`ExceptionManager` handle a stack of :keyword:`ExceptionHandler`. By default, PyMT have only one instance of this class, available with :keyword:`pymt_exception_manager`.

The handler
-----------

Extend the :keyword:`ExceptionHandler` to create your own handler ::

    class MyExceptionHandler(ExceptionHandler):
        def handle_exception(self, exception):
            print 'Exception catched in my handler', exception
            return ExceptionManager.RAISE


And use :keyword:`ExceptionHandler.add_handler()` on the manager to add your handler in the stack ::

    pymt_exception_manager.add_handler(MyExceptionHandler())

Only 2 possibility are available when a exception is catched :

* Raise it : :keyword:`ExceptionManager.RAISE`
* Ignore it : :keyword:`ExceptionManager.PASS`
