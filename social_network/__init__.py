# social_network/__init__.py
import email.charset

# Устанавливаем правильную кодировку для писем
email.charset.add_charset('utf-8', email.charset.QP, email.charset.QP, 'utf-8')