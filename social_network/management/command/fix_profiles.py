from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from social_network.models import Profile


class Command(BaseCommand):
    help = 'Исправляет дублирующиеся профили пользователей'

    def handle(self, *args, **options):
        self.stdout.write('Поиск дублирующихся профилей...')

        fixed = 0
        for user in User.objects.all():
            profiles = Profile.objects.filter(user=user)

            if profiles.count() > 1:
                self.stdout.write(f'Найдено {profiles.count()} профилей для пользователя {user.username}')
                # Удаляем все кроме первого
                for profile in profiles[1:]:
                    profile.delete()
                    self.stdout.write(f'  Удален дубликат профиля ID {profile.id}')
                fixed += 1

            elif profiles.count() == 0:
                self.stdout.write(f'Для пользователя {user.username} нет профиля, создаю...')
                Profile.objects.create(user=user)
                fixed += 1

        self.stdout.write(self.style.SUCCESS(f'\nИсправлено {fixed} профилей'))
        self.stdout.write(f'Пользователей: {User.objects.count()}')
        self.stdout.write(f'Профилей: {Profile.objects.count()}')