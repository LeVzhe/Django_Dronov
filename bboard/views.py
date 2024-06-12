from django.http import HttpResponse

#КОНТРОЛЛЕРЫ
def index(request):
    return HttpResponse('Здесь будет выведен список объявлений.')

def t_index(request):
    return HttpResponse('Проверка Test')