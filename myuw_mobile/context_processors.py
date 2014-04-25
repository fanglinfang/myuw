from django.conf import settings

def has_less_compiled(request):
    """ See if django-compressor is being used to precompile less
    """
    key = getattr(settings, "COMPRESS_PRECOMPILERS", None)
    return {'has_less_compiled': key != ()}


def less_not_compiled(request):
    return { }