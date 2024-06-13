from django.shortcuts import render

from .models import Bb

#КОНТРОЛЛЕРЫ
def index(request):
    bbs = Bb.objects.order_by('-published')
    return render(request, 'bboard/index.html', {'bbs': bbs})

def t_index(request):
    bbs = ['1', '2', '3']
    return render(request, 'bboard/index.html', {'bbs': bbs})