from django.contrib import admin
from .models import Profile, Post, Comment, Friendship


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio', 'location']
    search_fields = ['user__username', 'bio', 'location']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'content_preview', 'created_at', 'total_likes']
    list_filter = ['created_at', 'author']
    search_fields = ['content', 'author__username']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    content_preview.short_description = 'Контент'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post_preview', 'content_preview', 'created_at']
    list_filter = ['created_at']

    def post_preview(self, obj):
        return obj.post.content[:30] + '...' if len(obj.post.content) > 30 else obj.post.content

    post_preview.short_description = 'Пост'

    def content_preview(self, obj):
        return obj.content[:30] + '...' if len(obj.content) > 30 else obj.content

    content_preview.short_description = 'Комментарий'


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['from_user__username', 'to_user__username']