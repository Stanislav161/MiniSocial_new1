from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
import os


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='avatars/', blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return f'Профиль {self.user.username}'

    def get_profile_picture_url(self):
        """Возвращает URL аватарки или None"""
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return None

    def save(self, *args, **kwargs):
        # Сначала сохраняем, чтобы получить путь к файлу
        super().save(*args, **kwargs)

        # Оптимизация изображения профиля (если оно есть и не default)
        if self.profile_picture and self.profile_picture.name != 'avatars/default.png':
            try:
                img_path = self.profile_picture.path
                if os.path.exists(img_path):
                    img = Image.open(img_path)
                    if img.height > 300 or img.width > 300:
                        output_size = (300, 300)
                        img.thumbnail(output_size)
                        img.save(img_path)
            except Exception as e:
                # Игнорируем ошибки с изображениями
                print(f"Ошибка при обработке изображения: {e}")

    def follow(self, user_profile):
        """Подписаться на пользователя"""
        if self.user != user_profile.user:
            Follow.objects.get_or_create(
                follower=self.user,
                following=user_profile.user
            )

    def unfollow(self, user_profile):
        """Отписаться от пользователя"""
        Follow.objects.filter(
            follower=self.user,
            following=user_profile.user
        ).delete()

    def is_following(self, user):
        """Проверяет, подписан ли текущий пользователь на другого"""
        return Follow.objects.filter(
            follower=self.user,
            following=user
        ).exists()

    def get_following_count(self):
        """Количество подписок"""
        return self.user.following.count()

    def get_followers_count(self):
        """Количество подписчиков"""
        return self.user.followers.count()


#@receiver(post_save, sender=User)
#def create_or_update_user_profile(sender, instance, created, **kwargs):
#    """
#    Создает профиль при создании пользователя или обновляет при сохранении.
#    """
#    if created:
#        # При создании пользователя - создаем профиль
#        Profile.objects.create(user=instance)
#    else:
#        # При обновлении пользователя - обновляем профиль если он существует
#        try:
#            instance.profile.save()
#        except Profile.DoesNotExist:
#            # Если профиля почему-то нет - создаем
#            Profile.objects.create(user=instance)

#@receiver(post_save, sender=User)
#def handle_user_profile(sender, instance, created, **kwargs):
#   """
#    Обрабатывает создание и обновление профиля пользователя.
#    """
#    if created:
#        # При создании пользователя - создаем профиль
#        Profile.objects.create(user=instance)
#    else:
#        # При обновлении пользователя - НЕ СОЗДАЕМ профиль,
#        # только сохраняем если он существует
#        try:
#            instance.profile.save()
#        except Profile.DoesNotExist:
#            # Если профиля нет - ничего не делаем
#            # (он должен был создаться при создании пользователя)
#            pass


# models.py - УДАЛИТЕ ВСЕ СУЩЕСТВУЮЩИЕ СИГНАЛЫ И ДОБАВЬТЕ ЭТОТ:

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Создает профиль только при создании нового пользователя.
    Используем get_or_create для безопасности.
    """
    if created:
        Profile.objects.get_or_create(user=instance)
    # При обновлении пользователя ничего не делаем - профиль не трогаем


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Сохраняет профиль при сохранении пользователя"""
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)


class Follow(models.Model):
    """Модель для подписок (кто на кого подписан)"""
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'  # те, на кого я подписан
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers'  # те, кто подписан на меня
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['follower', 'following']  # чтобы не было дублей
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.follower.username} подписан на {self.following.username}'


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Пост от {self.author.username}'

    def total_likes(self):
        return self.likes.count()

    def get_image_url(self):
        """Возвращает URL изображения поста или None"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return None


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Комментарий от {self.author.username}'


class Friendship(models.Model):
    STATUS_CHOICES = (
        ('pending', 'В ожидании'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено'),
    )

    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['from_user', 'to_user']

    def __str__(self):
        return f'{self.from_user.username} -> {self.to_user.username}: {self.status}'