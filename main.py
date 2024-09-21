from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routes import contacts, auth, users
from typing import Dict

# Завантажує змінні середовища з файлу .env
load_dotenv()

# Ініціалізація FastAPI додатка
app = FastAPI()

# Налаштування CORS (Cross-Origin Resource Sharing) для додатка
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Дозволяє всі джерела
    allow_credentials=True,
    allow_methods=["*"],  # Дозволяє всі HTTP методи
    allow_headers=["*"],  # Дозволяє всі заголовки
)


# Включення роутерів для різних частин додатка (контакти, авторизація, користувачі)
app.include_router(contacts.router, prefix='/api')
app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')


@app.get("/")
def read_root() -> Dict[str, str]:
    """
    Базовий роут для перевірки роботи сервера.

    :return: Словник із привітальним повідомленням.
    :rtype: Dict[str, str]
    """
    return {"message": "Hello World"}
