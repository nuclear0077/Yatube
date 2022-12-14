from core.utils import paginate_page
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


@cache_page(20, key_prefix='index_page')
def index(request):
    posts_list = Post.objects.select_related('author', 'group')
    page_obj = paginate_page(request=request, posts_list=posts_list)
    context = {'page_obj': page_obj}
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.select_related('author', 'group')
    page_obj = paginate_page(request=request, posts_list=posts_list)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    check_subscribes = None
    author = get_object_or_404(User, username=username)
    posts_list = author.posts.select_related('author', 'group')
    page_obj = paginate_page(request=request, posts_list=posts_list)
    if request.user.is_authenticated:
        check_subscribes = author.following.filter(user=request.user).exists()
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': check_subscribes,
        'subscription_ban': author == request.user,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.select_related('author')
    form = CommentForm(request.POST or None)
    context = {'post': post, 'comments': comments, 'form': form}
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not request.method == 'POST':
        return render(request, 'posts/create_post.html', {'form': form})
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', request.user)


@login_required
def post_edit(request, post_id):
    posts = get_object_or_404(Post, id=post_id)
    if request.user != posts.author:
        return redirect("posts:post_detail", post_id)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=posts
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {'form': form, 'is_edit': True}
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts_list = Post.objects.filter(
        author__following__user=request.user.id
    ).select_related('author', 'group')
    page_obj = paginate_page(request=request, posts_list=posts_list)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if not request.user != author:
        return redirect('posts:profile', username=username)
    check_follower = Follow.objects.filter(user=request.user, author=author)
    if check_follower.exists():
        return redirect('posts:profile', username=username)
    follow = Follow.objects.create(author=author, user=request.user)
    follow.save()
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user_follower = Follow.objects.filter(author=author, user=request.user)
    user_follower.delete()
    return redirect('posts:profile', username=username)
