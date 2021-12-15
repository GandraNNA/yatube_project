from django.shortcuts import render
from django.http import HttpResponse


# Main page
def index(request):
    template = 'posts/index.html'
    title = 'Yatube'
    text = 'Это главная страница проекта Yatube'
    context = {
        'title': title,
        'text': text,
    }
    return render(request, template, context)


# Page with posts, filtered by groups
def group_posts(request):
    template = 'posts/group_list.html'
    title = 'Информация о группах проекта Yatube'
    text = 'Здесь будет информация о группах проекта Yatube'
    context = {
        'title': title,
        'text': text,
    }
    return render(request, template, context)
