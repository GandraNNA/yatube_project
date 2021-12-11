# from django.shortcuts import render
from django.http import HttpResponse


# Main page
def index(request):
    return HttpResponse('Main page')


# Page with posts, filtered by groups
def group_posts(request, slug):
    return HttpResponse('Posts, filtered by groups')
