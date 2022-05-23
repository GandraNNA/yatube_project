from http import HTTPStatus

from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
# from django.core.mail import send_mail
from django.urls import reverse_lazy

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow


def index(request):
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    text = 'Последние обновления на сайте'
    image = Post.image
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.NUMBER_OF_POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'title': title,
        'text': text,
        'image': image,
    }
    return render(
        request,
        template,
        context
    )


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.order_group_posts.all()
    paginator = Paginator(post_list, settings.NUMBER_OF_POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    image = Post.image
    context = {
        'group': group,
        'page_obj': page_obj,
        'image': image,
    }
    return render(
        request,
        template,
        context
    )


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    title = 'Профайл пользователя ' + author.get_full_name()
    post_list = author.posts.all()
    paginator = Paginator(post_list, settings.NUMBER_OF_POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    image = Post.image
    current_user = request.user
    if current_user.is_authenticated and current_user != author:
        following = Follow.objects.filter(
            user=current_user, author=author).exists()
    else:
        following = False
    context = {
        'page_obj': page_obj,
        'title': title,
        'author': author,
        'post_list': post_list,
        'image': image,
        'following': following,
    }
    return render(request,
                  template,
                  context
                  )


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = Post.objects.filter(pk=post_id).first()
    title = 'Пост ' + post.text[:15]
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    image = Post.image
    context = {
        'post': post,
        'form': form,
        'comments': comments,
        'title': title,
        'image': image,
    }
    return render(request,
                  template,
                  context
                  )


@login_required
def create_post(request):
    template = 'posts/create_post.html'
    title = 'Новая запись'
    header = 'Добавить запись'
    form = PostForm(data=request.POST or None,
                    files=request.FILES or None)
    id_group = Group.objects.all()
    if request.method == 'POST':

        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect(
                reverse_lazy(
                    'posts:profile',
                    args=(request.user.username,)
                )
            )
        else:
            form = render(request,
                          template,
                          {'form': form}
                          )

    context = {
        'title': title,
        'header': header,
        'id_group': id_group,
        'form': form,
    }
    return render(
        request,
        template,
        context
    )


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html',
    title = 'Редактировать запись'
    header = 'Редактировать запись'
    post = get_object_or_404(
        Post,
        pk=post_id
    )

    if post.author != request.user:
        return redirect(reverse_lazy(
            'posts:post_detail',
            args=(post.pk,)))

    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
        if form.is_valid():
            form.save()
            return redirect(
                reverse_lazy(
                    'posts:post_detail',
                    args=(post.pk,))
            )
        else:
            return render(
                request,
                template,
                {'form': form}
            )

    form = PostForm(initial={'text': post.text})
    context = {
        'title': title,
        'header': header,
        'post_edit': True,
        'form': form,
    }
    return render(
        request,
        template,
        context
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post.pk)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    current_user = request.user
    title = 'Подписки'
    text = 'Посты по подпискам'
    post_list = Post.objects.filter(
        author__following__user=current_user)
    paginator = Paginator(post_list, settings.NUMBER_OF_POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'title': title,
        'text': text,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user, author=author
        )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.filter(
            user=request.user, author=author
        ).delete()
    return redirect('posts:profile', username=author.username)
