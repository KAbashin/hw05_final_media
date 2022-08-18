from django.shortcuts import render


def index(request):
    """ Главная страница """
    template = 'posts/index.html'
    return render(request, template)
