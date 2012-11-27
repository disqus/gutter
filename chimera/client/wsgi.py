from chimera.client import signals
from werkzeug.local import Local


class EnabledSwitchesMiddleware(object):
    """
    Middleware to add active chimera switches for the HTTP request in a
    X-Chimera-Switch headers.

    NOTE: This middleware breaks streaming responses.  Since it is impossible
    to determine the active switches used for an HTTP response until the entire
    response body has been read, this middleware buffers the entire reponse body
    into memory, then adds the X-Chimera-Switch header, before returning.
    """

    def __init__(self, application, chimera=None):
        self.application = application

        if not chimera:
            from chimera.client.singleton import chimera

        self.chimera = chimera
        self.locals = Local()

        self.locals.on_switch_active = self.__signal_handler
        signals.switch_active.connect(self.locals.on_switch_active)

    def __signal_handler(self, switch, inpt):
        self.locals.switches_active.append(switch.name)

    def __call__(self, environ, start_response):
        self.locals.switches_active = []
        body, status, headers = self.__call_app(environ, start_response)
        self.__add_chimera_header_to(headers)

        start_response(status, headers)
        return body

    def __add_chimera_header_to(self, headers):
        active_switches = ','.join(self.locals.switches_active)
        headers.append(('X-Chimera-Switch', 'active=%s' % active_switches))

    def __call_app(self, environ, start_response):
        status_headers = [None, None]
        body = []

        def capture_start_response(status, headers):
            status_headers[:] = (status, headers)
            return body.append

        map(body.append, self.application(environ, capture_start_response))

        return (body,) + tuple(status_headers)
