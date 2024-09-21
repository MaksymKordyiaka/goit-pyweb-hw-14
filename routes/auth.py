from fastapi import APIRouter, HTTPException, status, Depends, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from schemas import UserCreate, UserResponse, TokenModel, RequestEmail
from db.connect_db import get_db
from services.auth import auth_services
from services.email import send_email
import repository

router = APIRouter()
security = HTTPBearer()


@router.post('/register', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    Реєструє нового користувача.

    :param user: Дані користувача для реєстрації.
    :type user: UserCreate
    :param background_tasks: Фонова задача для надсилання email підтвердження.
    :type background_tasks: BackgroundTasks
    :param request: HTTP-запит, необхідний для отримання базового URL.
    :type request: Request
    :param db: Сеанс бази даних.
    :type db: Session
    :return: Об'єкт нового користувача.
    :rtype: UserResponse
    :raises HTTPException: Якщо email вже зареєстрований.
    """
    exist_user = repository.users.get_user_by_email(user.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email already registered')
    user.password = auth_services.hash_password(user.password)
    new_user = repository.users.create_user(db, user)
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)
    return new_user


@router.post('/login', response_model=TokenModel, status_code=status.HTTP_201_CREATED)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Авторизація користувача за допомогою email та пароля.

    :param db: Сеанс бази даних.
    :type db: Session
    :param form_data: Форма для аутентифікації, яка містить email і пароль.
    :type form_data: OAuth2PasswordRequestForm
    :return: Токени доступу та оновлення.
    :rtype: TokenModel
    :raises HTTPException: Якщо email не знайдено, не підтверджений, або пароль невірний.
    """
    user = repository.users.get_user_by_email(form_data.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_services.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    access_token = auth_services.create_access_token(data={'sub': user.email})
    refresh_token = auth_services.create_refresh_token(data={'sub': user.email})
    repository.users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post('/request_email')
def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                  db: Session = Depends(get_db)):
    """
    Надсилає користувачу email для підтвердження його адреси.

    :param body: Тіло запиту з email користувача.
    :type body: RequestEmail
    :param background_tasks: Фонова задача для надсилання email.
    :type background_tasks: BackgroundTasks
    :param request: HTTP-запит для отримання базового URL.
    :type request: Request
    :param db: Сеанс бази даних.
    :type db: Session
    :return: Повідомлення про успіх операції.
    :rtype: dict
    """
    user = repository.users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}


@router.get('/refresh_token', response_model=TokenModel, status_code=status.HTTP_201_CREATED)
def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    Оновлює токен доступу, використовуючи рефреш токен.

    :param credentials: Токен рефрешу, наданий через заголовок авторизації.
    :type credentials: HTTPAuthorizationCredentials
    :param db: Сеанс бази даних.
    :type db: Session
    :return: Нові токени доступу та оновлення.
    :rtype: TokenModel
    :raises HTTPException: Якщо рефреш токен недійсний або не відповідає запису в базі даних.
    """
    token = credentials.credentials
    email = auth_services.decode_refresh_token(token)
    user = repository.users.get_user_by_email(email, db)
    if user.refresh_token != token:
        repository.users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = auth_services.create_access_token(data={"sub": email})
    refresh_token = auth_services.create_refresh_token(data={"sub": email})
    repository.users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Підтверджує email користувача за допомогою токена підтвердження.

    :param token: Токен підтвердження, отриманий через email.
    :type token: str
    :param db: Сеанс бази даних.
    :type db: Session
    :return: Повідомлення про успіх підтвердження.
    :rtype: dict
    :raises HTTPException: Якщо токен недійсний або користувач не знайдений.
    """
    email = auth_services.get_email_from_token(token)
    user = repository.users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    repository.users.confirmed_email(email, db)
    return {"message": "Email confirmed"}
