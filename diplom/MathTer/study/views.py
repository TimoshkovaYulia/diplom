from django.http import HttpResponse


def index(request):
    return HttpResponse("Привет, мир. Ты на странице с результатами голосования.")