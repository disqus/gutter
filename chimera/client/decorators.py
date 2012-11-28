from functools import wraps
from chimera.client.singleton import chimera as default_chimera
from django.http import Http404, HttpResponseRedirect


def switch_active(name, redirect_to=None, chimera=None):

    if not chimera:
        chimera = default_chimera

    def inner(func):

        @wraps(func)
        def view(request, *args, **kwargs):
            if chimera.active(name, request):
                return func(request, *args, **kwargs)
            elif redirect_to:
                return HttpResponseRedirect(redirect_to)
            else:
                raise Http404('Switch %s not active' % name)

        return view

    return inner
