import os
from datetime import timedelta, datetime
from dotenv import load_dotenv
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from db.connect_db import get_db
from repository import users

load_dotenv()


class Auth:
    """
    Клас для обробки аутентифікації, включаючи хешування паролів, створення та перевірку токенів.

    Атрибути:
        pwd_context (CryptContext): Контекст для хешування паролів за допомогою bcrypt.
        SECRET_KEY (str): Секретний ключ для кодування та декодування JWT токенів.
        ALGORITHM (str): Алгоритм, який використовується для кодування та декодування JWT токенів.
        oauth2_scheme (OAuth2PasswordBearer): Залежність для OAuth2 password flow.
    """

    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

    def hash_password(self, password: str) -> str:
        """
        Хешує простий пароль.

        :param password: Простой пароль для хешування.
        :type password: str
        :return: Хешований пароль.
        :rtype: str
        """
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Перевіряє простий пароль проти хешованого пароля.

        :param plain_password: Простий пароль для перевірки.
        :type plain_password: str
        :param hashed_password: Хешований пароль для перевірки.
        :type hashed_password: str
        :return: True, якщо паролі збігаються, інакше False.
        :rtype: bool
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        """
        Створює JWT токен для доступу.

        :param data: Дані для кодування в токені.
        :type data: dict
        :param expires_delta: Часове зсув для закінчення терміну дії токену. Якщо None, за замовчуванням - 30 хвилин.
        :type expires_delta: timedelta, optional
        :return: Закодований токен доступу.
        :rtype: str
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=30)
        to_encode.update({'exp': expire, 'scope': 'access_token'})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    def create_refresh_token(self, data: dict, expires_delta: timedelta = None):
        """
        Створює JWT токен для поновлення.

        :param data: Дані для кодування в токені.
        :type data: dict
        :param expires_delta: Часове зсув для закінчення терміну дії токену. Якщо None, за замовчуванням - 7 днів.
        :type expires_delta: timedelta, optional
        :return: Закодований токен поновлення.
        :rtype: str
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({'exp': expire, 'scope': 'refresh_token'})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    def decode_refresh_token(self, refresh_token: str):
        """
        Декодує та перевіряє токен поновлення.

        :param refresh_token: Токен поновлення для декодування.
        :type refresh_token: str
        :return: Електронна пошта, закодована в токені, якщо вона дійсна.
        :rtype: str
        :raises HTTPException: Якщо токен недійсний або область не відповідає.
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        Отримує поточного користувача на основі наданого токену доступу.

        :param token: Токен доступу для декодування.
        :type token: str
        :param db: Залежність для сесії бази даних.
        :type db: Session
        :return: Користувач, пов'язаний з токеном.
        :rtype: User
        :raises HTTPException: Якщо токен недійсний або користувача не існує.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user

    def create_email_token(self, data: dict):
        """
        Створює JWT токен для підтвердження електронної пошти.

        :param data: Дані для кодування в токені.
        :type data: dict
        :return: Закодований токен для підтвердження електронної пошти.
        :rtype: str
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    def get_email_from_token(self, token: str):
        """
        Отримує електронну пошту з токена.

        :param token: Токен для декодування.
        :type token: str
        :return: Електронна пошта, закодована в токені.
        :rtype: str
        :raises HTTPException: Якщо токен недійсний для підтвердження електронної пошти.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload.get("sub")
            return email
        except JWTError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")


auth_services = Auth()
