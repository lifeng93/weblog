from django.http import Http404
import re

def referer_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        referer = request.META.get('HTTP_REFERER')
        if referer:
            re_pattern = '^(?=^.{3,255}$)(http(s)?:\/\/)?(www\.)?[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+(:[0-9]{1,5})?'
            dns = re.match(re_pattern, referer).group()
            allow_host = ['http://'+request.META['HTTP_HOST']]
            if dns in allow_host:
                return view_func(request,  *args, **kwargs)
            else:
                raise Http404
        else:
            raise Http404
    return _wrapped_view


def ajax_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.is_ajax():
            return view_func(request,  *args, **kwargs)
        else:
            raise Http404
    return _wrapped_view
