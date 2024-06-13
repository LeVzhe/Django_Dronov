from django.http import HttpResponse

from .models import Bb

#КОНТРОЛЛЕРЫ
def index(request):
    s = 'Объявления\r\n\r\n\r\n'
    for bb in Bb.objects.order_by('-published'):
        s += bb.title + '\r\n' + bb.content + '\r\n\r\n'
    return HttpResponse(s, content_type='text/plain; charset=utf-8')

def t_index(request):
    return HttpResponse('Проверка Test')