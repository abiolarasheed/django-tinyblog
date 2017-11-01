# -*- coding: utf-8 -*-
from django.http.response import JsonResponse


def ajax_required(view_function):
    """
    AJAX request required decorator
    use it in your views:
    """
    def wrap(request, *args, **kwargs):
        if not request.is_ajax():
            return JsonResponse({'message': "Bad Request"},
                                status=400)
        return view_function(request, *args, **kwargs)
    wrap.__doc__ = view_function.__doc__

    try:
        wrap.__name__ = view_function.__name__
    except AttributeError:
        """If for some reason the view has no name we move on."""
        pass

    return wrap
