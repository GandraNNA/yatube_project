from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
# from django.core.mail import send_mail
from django.urls import reverse_lazy

from .forms import PostForm
from .models import Group, Post, User


def index(request):
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    text = 'Последние обновления на сайте'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'title': title,
        'text': text,
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
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
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
    post_user_list = Post.objects.select_related('author', 'group').all()
    number_of_posts = post_user_list.count()
    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'title': title,
        'author': author,
        'number_of_posts': number_of_posts,
        'post_list': post_list,
    }
    return render(request,
                  template,
                  context
                  )


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = Post.objects.filter(pk=post_id).first()
    title = 'Пост ' + post.text[:15]
    context = {
        'post': post,
        'title': title,
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
    form = PostForm(data=request.POST)
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
            data=request.POST,
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
