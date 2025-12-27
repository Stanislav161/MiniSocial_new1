from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# ДОБАВЬТЕ ЭТОТ ИМПОРТ И КЛАСС
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect


# social_network/views.py - обновленный CustomLoginView
class CustomLoginView(LoginView):
    template_name = 'social_network/login.html'

    def get_success_url(self):
        user = self.request.user

        # 1. ТОЛЬКО пользователь superadmin идет в Django Admin
        if user.username == 'superadmin':
            return '/admin/'

        return '/'

from .forms import UserRegisterForm, ProfileUpdateForm, UserUpdateForm, PostForm
from .models import Post, Friendship, Comment, Follow, Profile


def index(request):
    if request.user.is_authenticated:
        posts = Post.objects.all().order_by('-created_at')[:10]
        return render(request, 'social_network/feed.html', {'posts': posts})
    return render(request, 'social_network/index.html')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                Profile.objects.get_or_create(user=user)
                login(request, user)
                messages.success(request, f'Аккаунт создан для {user.username}!')
                return redirect('home')
            except Exception as e:
                messages.error(request, f'Ошибка при создании аккаунта: {str(e)}')
                return render(request, 'social_network/register.html', {'form': form})
    else:
        form = UserRegisterForm()
    return render(request, 'social_network/register.html', {'form': form})


@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user).order_by('-created_at')

    # Проверка подписки
    is_following = False
    if request.user != user:
        is_following = Follow.objects.filter(
            follower=request.user,
            following=user
        ).exists()

    return render(request, 'social_network/profile.html', {
        'profile_user': user,
        'posts': posts,
        'posts_count': posts.count(),
        'is_following': is_following,
        'followers_count': user.followers.count(),
        'following_count': user.following.count(),
    })


@login_required
def profile_edit(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Ваш профиль обновлен!')
            return redirect('profile', username=request.user.username)
        else:
            for field, errors in p_form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'social_network/profile_edit.html', {
        'u_form': u_form,
        'p_form': p_form,
    })


@login_required
def feed(request):
    """Лента новостей с пагинацией"""
    feed_type = request.GET.get('feed', 'following')
    page_number = request.GET.get('page', 1)

    # ОТЛАДОЧНЫЙ ВЫВОД
    print(f"\n=== DEBUG FEED FUNCTION ===")
    print(f"Requested feed_type: '{feed_type}'")
    print(f"User: {request.user.username}")
    print(f"User following count: {request.user.following.count()}")

    if feed_type == 'following':
        following_users = User.objects.filter(followers__follower=request.user)
        print(f"Following users found: {following_users.count()}")
        for user in following_users:
            print(f"  - {user.username}")

        posts_list = Post.objects.filter(author__in=following_users)
        feed_title = "Лента подписок"
    else:
        posts_list = Post.objects.all()
        feed_title = "Все посты"

    print(f"Total posts in list: {posts_list.count()}")
    print(f"Feed title: {feed_title}")
    print(f"=== END DEBUG ===\n")

    posts_list = posts_list.order_by('-created_at')
    paginator = Paginator(posts_list, 10)

    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'social_network/feed.html', {
        'posts': posts,
        'feed_type': feed_type,
        'feed_title': feed_title,
        'is_paginated': posts.has_other_pages(),
        'page_obj': posts,
    })


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Пост опубликован!')
            return redirect('feed')
    else:
        form = PostForm()
    return render(request, 'social_network/create_post.html', {'form': form})


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'social_network/post_detail.html', {'post': post})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            if 'remove_image' in request.POST and request.POST['remove_image'] == 'on':
                if post.image:
                    post.image.delete(save=False)
                    post.image = None
            form.save()
            messages.success(request, 'Пост обновлен!')
            return redirect('feed')
    else:
        form = PostForm(instance=post)

    return render(request, 'social_network/post_edit.html', {'form': form, 'post': post})


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)

    if request.method == 'POST':
        if post.image:
            post.image.delete(save=False)
        post.delete()
        messages.success(request, 'Пост удален!')
        return redirect('feed')

    return render(request, 'social_network/post_delete.html', {'post': post})


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
        messages.info(request, 'Лайк удален')
    else:
        post.likes.add(request.user)
        messages.success(request, 'Посту поставлен лайк')

    return redirect('feed')


@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)

    if request.user != user_to_follow:
        Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )
        messages.success(request, f'Вы подписались на {username}')

    return redirect('profile', username=username)


@login_required
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)

    Follow.objects.filter(
        follower=request.user,
        following=user_to_unfollow
    ).delete()

    messages.success(request, f'Вы отписались от {username}')
    return redirect('profile', username=username)


@login_required
def following_list(request, username):
    """Список подписок пользователя"""
    user = get_object_or_404(User, username=username)
    following = User.objects.filter(followers__follower=user)

    return render(request, 'social_network/following_list.html', {
        'profile_user': user,
        'following': following,
        'is_own_profile': request.user == user,
    })


@login_required
def followers_list(request, username):
    """Список подписчиков пользователя"""
    user = get_object_or_404(User, username=username)
    followers = User.objects.filter(following__following=user)

    return render(request, 'social_network/followers_list.html', {
        'profile_user': user,
        'followers': followers,
        'is_own_profile': request.user == user,
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()

        if content:
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content
            )
            messages.success(request, 'Комментарий добавлен!')
        else:
            messages.error(request, 'Комментарий не может быть пустым')

    return redirect(request.META.get('HTTP_REFERER', 'feed'))


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.author != request.user:
        messages.error(request, 'Вы можете удалять только свои комментарии')
        return redirect('feed')

    post_id = comment.post.id
    comment.delete()
    messages.success(request, 'Комментарий удален')

    return redirect('post_detail', post_id=post_id)