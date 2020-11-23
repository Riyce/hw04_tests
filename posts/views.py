from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Group, Post, User
from .forms import PostForm
from django.core.paginator import Paginator


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    ) 

def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
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
    if request.method == "POST":
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect('index')
        return render(request, 'new.html', {'form': form})
    return render(request, 'new.html', {'form': form})

def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'profile.html',
        {'author': author, 'page': page, 'paginator': paginator}
    ) 

def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=author)
    return render(
        request, 
        'post.html', 
        {'post': post, 'author': author}
    )

def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id)
    if request.user == author:
        if request.method == 'POST':
            form = PostForm(request.POST, instance=post)
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
                {'form': form, 'post': post}
            )
        return render(
            request, 
            'new.html',
            {'form': PostForm(instance=post), 'post': post}
        )
    else:
        return redirect(
            'post',
            username=username,
            post_id=post_id,
        )