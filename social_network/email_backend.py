# social_network/email_backend.py
# social_network/email_backend.py
from django.core.mail.backends.console import EmailBackend as ConsoleEmailBackend
import sys
import io
import base64


class UnicodeConsoleEmailBackend(ConsoleEmailBackend):
    """Кастомный EmailBackend для правильного отображения русских писем в консоли"""

    def write_message(self, message):
        print("\n" + "=" * 80)
        print("📧 ПИСЬМО ДЛЯ СБРОСА ПАРОЛЯ 📧")
        print("=" * 80)

        try:
            # Получаем тело письма
            body = message.body

            # Проверяем кодировку через заголовки
            content_transfer_encoding = None
            for header, value in message.extra_headers.items():
                if header.lower() == 'content-transfer-encoding':
                    content_transfer_encoding = value
                    break

            # Если не нашли в extra_headers, проверяем в message._headers
            if not content_transfer_encoding and hasattr(message, '_headers'):
                for header, value in message._headers:
                    if header.lower() == 'content-transfer-encoding':
                        content_transfer_encoding = value
                        break

            # Если письмо в base64 - декодируем
            if body and content_transfer_encoding == 'base64':
                try:
                    # Убираем переносы строк в base64
                    body_clean = body.replace('\n', '').replace('\r', '')
                    body_decoded = base64.b64decode(body_clean).decode('utf-8')
                    print(body_decoded)
                except Exception as e:
                    print(f"Ошибка декодирования base64: {e}")
                    print("Оригинальный текст:")
                    print(body)
            else:
                print(body)

        except Exception as e:
            print(f"Ошибка при обработке письма: {e}")
            # Пытаемся просто вывести что есть
            if hasattr(message, 'body'):
                print(message.body)
            elif hasattr(message, 'message'):
                try:
                    print(message.message().get_payload())
                except:
                    print("Не удалось получить содержимое письма")

        print("=" * 80 + "\n")