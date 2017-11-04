# -*- coding: utf-8 -*-
import os
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


class FileUploader:
    """
    This class helps set the filename and pat, for a file like field and
      gives us the possibility of extending it and adding more functionalities
      for different backends, dynamic nameing paths and filename.

      Usage: class MyModel(models.Model):
                 image = models.ImageField(upload_to=FileUploader())
    """
    pass
