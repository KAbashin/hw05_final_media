from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .models import Group, Post, User, Follow
from .forms import PostForm, CommentForm

PAGE_POSTS = 10


def pagination(request, queryset):
    paginator = Paginator(queryset, PAGE_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'paginator': paginator,
        'page_namber': page_number,
        'page_obj': page_obj,
    }


@cache_page(20, key_prefix='index_page', )
def index(request):
    """ Главная страница """
    posts = Post.objects.all()
    paginator = Paginator(posts, PAGE_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/index.html'
    context = {
        'page_obj': page_obj,
        'posts': posts,
        'title': 'Последние обновления на сайте',
    }
    return render(request, template, context)


def group_posts(request, slug):
    """ Посты в группе """
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.g_posts.all()
    paginator = Paginator(posts, PAGE_POSTS)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        'group': group,
        'posts': posts,
        'title': slug,
    }
    return render(request, template, context)


def profile(request, username):
    """ профайл автора """
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    count = author.posts.count()
    paginator = Paginator(posts, PAGE_POSTS)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user,
                                          author=author).exists()
    context = {
        "page_obj": page_obj,
        "count": count,
        "author": author,
        "following": following,
    }
    template = "posts/profile.html"
    return render(request, template, context)


def post_detail(request, post_id):
    """ пост подробно """
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    comments = post.comments.all()
    post_title = post.text
    count = post.author.posts.count()
    author = post.author
    author_posts = author.posts.all().count()
    template = "posts/post_detail.html"
    context = {
        "post": post,
        "post_title": post_title,
        "author": author,
        "author_posts": author_posts,
        "form": form,
        "comments": comments,
        "count": count,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    """ создание нового поста """
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if request.method == "POST":
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', post.author)
    groups = Group.objects.all()
    template = "posts/create_post.html"
    context = {"form": form, "groups": groups}
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    """ редактирование поста """
    is_edit = True
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    groups = Group.objects.all()
    if request.user != author:
        return redirect("posts:post_detail", post_id)
    form = PostForm(
        request.POST or None,
        instance=post,
        files=request.FILES or None,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id)
    template = "posts/create_post.html"
    context = {
        "form": form,
        "is_edit": is_edit,
        "post": post,
        "groups": groups,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    """ добавление комментария к посту"""
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
    """ Главная страница с постами авторов на кого подписался"""
    post_list = Post.objects.filter(author__following__user=request.user)
    context = pagination(request, post_list)
    template = 'posts/follow.html'
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """ подписаться на автора"""
    user = request.user
    author = get_object_or_404(User, username=username)
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """ отписаться от автора """
    Follow.objects.filter(user=request.user,
                          author__username=username).delete()
    return redirect('posts:profile', username=username)
