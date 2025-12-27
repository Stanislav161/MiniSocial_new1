from django.core.mail import EmailMessage
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string


class UnicodePasswordResetForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        # Создаем тело письма из шаблона
        body = render_to_string(email_template_name, context)

        # Создаем тему письма
        subject = 'Восстановление пароля на MiniSocial'

        # Отправляем письмо с правильной кодировкой
        email = EmailMessage(
            subject,
            body,
            from_email,
            [to_email],
            headers={'Content-Type': 'text/plain; charset="utf-8"'}
        )
        email.send()