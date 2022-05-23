from {{ app_name }}.models import *
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response


def  (request):
    template_name = ''
    return render_to_response(
        template_name,
        {},
        context_instance=RequestContext(request)
    )
