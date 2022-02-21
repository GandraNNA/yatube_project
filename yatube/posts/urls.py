from . import views
from django.urls import path

# Создаём приложение Posts
app_name = 'Posts'

urlpatterns = [
    path('', views.index, name='index'),
    path('group/<slug>/', views.group_posts, name='group_list'),
]
