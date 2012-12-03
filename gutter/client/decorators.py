from functools import wraps
from gutter.client.singleton import gutter as default_gutter
from django.http import Http404, HttpResponseRedirect


def switch_active(name, redirect_to=None, gutter=None):

    if not gutter:
        gutter = default_gutter

    def inner(func):

        @wraps(func)
        def view(request, *args, **kwargs):
            if gutter.active(name, request):
                return func(request, *args, **kwargs)
            elif redirect_to:
                return HttpResponseRedirect(redirect_to)
            else:
                raise Http404('Switch %s not active' % name)

        return view

    return inner
