from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


def get_page(stack, request):
    return Paginator(stack, settings.LIMIT_OF_POSTS).get_page(
        request.GET.get('page')
    )


def index(request):
    """Функция представления главной страницы проекта
    Yatube, с учётом сортировки количества постов для
    текущего приложения
    """
    return render(request, 'posts/index.html', {
        'page_obj': get_page(Post.objects.all(), request),
    })


def group_posts(request, slug):
    """Функция представления страницы групп для проекта
    Yatube, с учётом сортировки количества постов для
    текущего приложения
    """
    group = get_object_or_404(Group, slug=slug)
    return render(request, 'posts/group_list.html', {
        'group': group,
        'page_obj': get_page(group.posts.all(), request),
    })


def profile(request, username):
    """Фунеция представления страницы пользователя"""
    author = get_object_or_404(User, username=username)
    return render(request, 'posts/profile.html', {
        'author': author,
        'page_obj': get_page(author.posts.all(), request),
    })


def post_detail(request, post_id):
    """Функция представления полной версии поста пользователя"""
    return render(request, 'posts/post_detail.html', {
        'post': get_object_or_404(Post, pk=post_id),
    })


@login_required
def post_create(request):
    """Функция представления страницы создания нового поста"""
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    new_post = form.save(commit=False)
    new_post.author = request.user
    new_post.save()
    return redirect('posts:profile', request.user)


@login_required
def post_edit(request, post_id):
    """Функция представления редактирования поста пользователя"""
    post = get_object_or_404(Post, pk=post_id)
    if not request.user == post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, instance=post)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {
            'form': form,
            'post': post,
        })
    form.save()
    return redirect('posts:post_detail', post_id)
