# create_test_fixed.py
import os
import sys
import django
from django.test import RequestFactory

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MiniSocial_new1.settings')
django.setup()

from django.test import Client
from social_network.models import User, Profile, Post
from django.contrib.auth import get_user_model


def test_fix_redirect_middleware():
    """Тест middleware для исправления редиректа"""
    print("Тестирование FixRedirectMiddleware...")

    # Тестируем напрямую класс middleware
    from social_network.middleware import FixRedirectMiddleware

    factory = RequestFactory()

    # Создаем mock-ответ с редиректом на '/'
    class MockResponse:
        def __init__(self):
            self.status_code = 302
            self.url = '/'  # Исходный URL, который должен быть исправлен

    # Mock функция get_response
    def mock_get_response(request):
        return MockResponse()

    # Создаем middleware
    middleware = FixRedirectMiddleware(mock_get_response)

    # Создаем тестовый запрос
    request = factory.get('/')

    # Вызываем middleware
    response = middleware(request)

    # Проверяем результат
    if response.url == '/ru/':
        print("✓ Middleware корректно исправил редирект с '/' на '/ru/'")
    else:
        print(f"✗ Ошибка: редирект не исправлен. URL: {response.url}")

    return response.url == '/ru/'


def test_main_page():
    """Тест главной страницы"""
    print("\n1. Тест главной страницы (неавторизованный):")

    client = Client()

    # Пробуем получить главную страницу
    try:
        response = client.get('/')
        print(f"   Статус: {response.status_code}")
        print(f"   Редирект: {response.url if hasattr(response, 'url') else 'Нет'}")
    except Exception as e:
        print(f"   Ошибка: {e}")
        return False

    return True


def main():
    print("=" * 50)
    print("ТЕСТИРОВАНИЕ MIDDLEWARE И СТРАНИЦ")
    print("=" * 50)

    # Запускаем тесты
    test1 = test_fix_redirect_middleware()
    test2 = test_main_page()

    print("\n" + "=" * 50)
    print("РЕЗУЛЬТАТЫ:")
    print(f"Middleware тест: {'ПРОЙДЕН' if test1 else 'НЕ ПРОЙДЕН'}")
    print(f"Главная страница: {'ДОСТУПНА' if test2 else 'ОШИБКА'}")
    print("=" * 50)


if __name__ == '__main__':
    main()