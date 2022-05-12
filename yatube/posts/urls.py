from django.urls import path

from . import views

app_name = 'Posts'

urlpatterns = [
    path(
        '',
        views.index,
        name='index'
    ),
    path(
        'group/<slug>/',
        views.group_posts,
        name='group_list'
    ),
    path(
        'profile/<str:username>/',
        views.profile,
        name='profile'
    ),
    path(
        'posts/<int:post_id>/',
        views.post_detail,
        name='post_detail'
    ),
    path(
        'create/',
        views.create_post,
        name='create_post'
    ),
    path(
        'posts/<int:post_id>/edit/',
        views.post_edit,
        name='post_edit'
    ),
    path(
        'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment'
    ),
]
