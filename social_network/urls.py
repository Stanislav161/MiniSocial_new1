from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import CustomLoginView  # ИМПОРТИРУЙТЕ CustomLoginView

urlpatterns = [
    # Основные
    path('', views.index, name='home'),
    path('register/', views.register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),  # ИСПОЛЬЗУЙТЕ CustomLoginView
    #path('login/', auth_views.LoginView.as_view(template_name='social_network/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    # Профиль
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/', views.profile, name='profile'),

    # СБРОС ПАРОЛЯ
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='social_network/password_reset.html',
             email_template_name='social_network/password_reset_email.html',
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='social_network/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='social_network/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),

    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='social_network/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    # Посты
    path('feed/', views.feed, name='feed'),
    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('post/<int:post_id>/delete/', views.post_delete, name='post_delete'),

    # Комментарии - ДОБАВЬТЕ ЭТИ СТРОКИ!
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

    # Подписки
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),
    path('profile/<str:username>/following/', views.following_list, name='following_list'),
    path('profile/<str:username>/followers/', views.followers_list, name='followers_list'),

    # Просмотр лайков поста - опционально
    #path('post/<int:post_id>/likes/', views.post_likes, name='post_likes'),
]