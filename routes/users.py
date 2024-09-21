import os
import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from db.connect_db import get_db
from db.models import User
from repository import users as repository_users
from services.auth import auth_services
from schemas import UserResponse
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(auth_services.get_current_user)):
    """
    Отримує дані поточного користувача.

    :param current_user: Поточний авторизований користувач.
    :type current_user: User
    :return: Дані поточного користувача.
    :rtype: UserResponse
    """
    return current_user


@router.patch('/avatar', response_model=UserResponse)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_services.get_current_user),
                             db: Session = Depends(get_db)):
    """
    Оновлює аватар поточного користувача за допомогою завантаження зображення в Cloudinary.

    :param file: Файл з новим аватаром.
    :type file: UploadFile
    :param current_user: Поточний авторизований користувач.
    :type current_user: User
    :param db: Сеанс бази даних.
    :type db: Session
    :return: Дані користувача з оновленим аватаром.
    :rtype: UserResponse
    """
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'NotesApp/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'NotesApp/{current_user.username}')\
                        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = repository_users.update_avatar(current_user.email, src_url, db)
    return user
