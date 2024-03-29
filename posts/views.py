from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


def index(request):
    list = Post.objects.all()
    paginator = Paginator(list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    list = group.posts.all()
    paginator = Paginator(list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        "group.html",
        {"group": group, 'page': page, 'paginator': paginator}
    )


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('index')
    return render(request, 'new.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    list = author.posts.all()
    paginator = Paginator(list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    name = 'profile'
    return render(
        request,
        'profile.html',
        {'author': author, 'page': page, 'paginator': paginator, 'name': name}
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    author = post.author
    name = 'post_view'
    return render(
        request,
        'post.html',
        {'post': post, 'author': author, 'name': name}
    )


def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    author = post.author
    if request.user != author:
        return redirect('post', username=username, post_id=post_id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect(
            'post',
            username=username,
            post_id=post_id
        )
    return render(
        request,
        'new.html',
        {'form': PostForm(instance=post), 'post': post}
    )
