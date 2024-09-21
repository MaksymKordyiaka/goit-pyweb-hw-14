import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr
from services.auth import auth_services

# Завантаження змінних середовища з файлу .env
load_dotenv()

# Конфігурація для підключення до сервера електронної пошти
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),  # Ім'я користувача для автентифікації на сервері електронної пошти
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),  # Пароль для автентифікації на сервері електронної пошти
    MAIL_FROM=os.getenv("MAIL_FROM"),  # Електронна пошта відправника
    MAIL_PORT=os.getenv("MAIL_PORT"),  # Порт сервера електронної пошти
    MAIL_SERVER=os.getenv("MAIL_SERVER"),  # Адреса сервера електронної пошти
    MAIL_FROM_NAME="Maks",  # Ім'я відправника, яке буде відображатися в листах
    MAIL_STARTTLS=False,  # Використовувати TLS для захищеного з'єднання
    MAIL_SSL_TLS=True,  # Використовувати SSL/TLS для захищеного з'єднання
    USE_CREDENTIALS=True,  # Використовувати автентифікацію для підключення
    VALIDATE_CERTS=True,  # Перевіряти сертифікати сервера
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',  # Шлях до папки з шаблонами електронних листів
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    Відправляє електронний лист для підтвердження електронної пошти.

    :param email: Електронна адреса отримувача.
    :type email: EmailStr
    :param username: Ім'я користувача для відображення в листі.
    :type username: str
    :param host: Базова URL адреса для підтвердження електронної пошти.
    :type host: str
    :raises ConnectionErrors: Якщо сталася помилка при з'єднанні з сервером електронної пошти.
    """
    try:
        # Створює токен для підтвердження електронної пошти
        token_verification = auth_services.create_email_token({"sub": email})

        # Створює повідомлення електронної пошти
        message = MessageSchema(
            subject="Confirm your email",  # Тема електронного листа
            recipients=[email],  # Отримувачі електронного листа
            template_body={"host": host, "username": username, "token": token_verification},
            # Тіло шаблону електронного листа
            subtype=MessageType.html  # Тип повідомлення (HTML)
        )

        # Ініціалізує FastMail з конфігурацією
        fm = FastMail(conf)

        # Відправляє електронний лист за допомогою шаблону
        await fm.send_message(message, template_name="email.html")
    except ConnectionErrors as err:
        # Виводить помилку у випадку проблем з підключенням
        print(err)
