from libgravatar import Gravatar
from sqlalchemy.orm import Session
from db.models import User
from schemas import UserCreate


def get_user_by_email(email: str, db: Session) -> User:
    """
    Retrieves a user from the database by their email address.

    :param email: The email address of the user to retrieve.
    :type email: str
    :param db: The database session used for querying the user.
    :type db: Session
    :return: The user object if found, or None if no user is associated with the provided email.
    :rtype: Optional[User]
    """
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: UserCreate) -> User:
    """
    Creates a new user with the provided details, including an optional Gravatar image.

    :param db: The database session used for adding the new user.
    :type db: Session
    :param user: The user creation schema with details like email, password, etc.
    :type user: UserCreate
    :return: The created user object.
    :rtype: User
    """
    avatar = None
    try:
        g = Gravatar(user.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**user.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Updates the refresh token for a specific user.

    :param user: The user whose token needs to be updated.
    :type user: User
    :param token: The new refresh token or None to clear it.
    :type token: str | None
    :param db: The database session used for committing changes.
    :type db: Session
    :return: None
    """
    user.refresh_token = token
    db.commit()


def confirmed_email(email: str, db: Session) -> None:
    """
    Marks a user's email as confirmed.

    :param email: The email address of the user to confirm.
    :type email: str
    :param db: The database session used for committing changes.
    :type db: Session
    :return: None
    """
    user = get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


def update_avatar(email: str, url: str, db: Session) -> User:
    """
    Updates the avatar of a user using a provided URL.

    :param email: The email address of the user whose avatar needs to be updated.
    :type email: str
    :param url: The URL of the new avatar image.
    :type url: str
    :param db: The database session used for committing changes.
    :type db: Session
    :return: The updated user object.
    :rtype: User
    """
    user = get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
