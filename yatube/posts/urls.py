from posts import views
from django.urls import path


# Создаём приложение Posts
app_name = 'Posts'

urlpatterns = [
    path('', views.index, name='main_page'),
    path('group_list.html', views.group_posts, name='group_list'),
]