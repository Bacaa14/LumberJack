from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.template import RequestContext
from django.shortcuts import redirect
from datetime import date

def index(request):
    if request.user.is_authenticated():
        template = loader.get_template('index.html')
        context = RequestContext(request, {
        })
        return HttpResponse(template.render(context))
    else:
        return redirect('accounts/login/')