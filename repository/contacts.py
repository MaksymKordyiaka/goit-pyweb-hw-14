from typing import Optional, List
from sqlalchemy import extract, cast, Date, and_
from sqlalchemy.orm import Session
from db.models import Contact, User
from schemas import ContactCreate
from datetime import date, timedelta


def get_contacts(db: Session, user: User, skip: int = 0, limit: int = 100) -> List[Contact]:
    """
    Retrieves a list of contacts for a specific user with pagination options.

    :param db: The database session.
    :type db: Session
    :param user: The user whose contacts are being retrieved.
    :type user: User
    :param skip: The number of contacts to skip. Default is 0.
    :type skip: int
    :param limit: The maximum number of contacts to return. Default is 100.
    :type limit: int
    :return: A list of contacts for the user.
    :rtype: List[Contact]
    """
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


def get_contact(db: Session, contact_id: int, user: User) -> Optional[Contact]:
    """
    Retrieves a specific contact by ID for a user.

    :param db: The database session.
    :type db: Session
    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param user: The user who owns the contact.
    :type user: User
    :return: The contact if found, or None.
    :rtype: Optional[Contact]
    """
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


def create_contact(db: Session, contact: ContactCreate, user: User) -> Contact:
    """
    Creates a new contact for a user.

    :param db: The database session.
    :type db: Session
    :param contact: The data for the new contact.
    :type contact: ContactCreate
    :param user: The user to whom the contact belongs.
    :type user: User
    :return: The created contact.
    :rtype: Contact
    """
    db_contact = Contact(**contact.dict(), user_id=user.id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def upgrade_contact(db: Session, user: User, contact_id: int, contact: ContactCreate) -> Optional[Contact]:
    """
    Updates an existing contact for a user.

    :param db: The database session.
    :type db: Session
    :param user: The user who owns the contact.
    :type user: User
    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param contact: The updated data for the contact.
    :type contact: ContactCreate
    :return: The updated contact, or None if not found.
    :rtype: Optional[Contact]
    """
    db_contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if db_contact:
        for key, value in contact.dict().items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact


def delete_contact(db: Session, user: User, contact_id: int) -> Optional[Contact]:
    """
    Deletes a contact for a specific user.

    :param db: The database session.
    :type db: Session
    :param user: The user who owns the contact.
    :type user: User
    :param contact_id: The ID of the contact to delete.
    :type contact_id: int
    :return: The deleted contact, or None if not found.
    :rtype: Optional[Contact]
    """
    db_contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
        return db_contact
    return None


def search_contacts(db: Session, user: User, first_name: Optional[str] = None,
                    second_name: Optional[str] = None, email: Optional[str] = None) -> List[Contact]:
    """
    Searches for contacts based on first name, last name, or email.

    :param db: The database session.
    :type db: Session
    :param user: The user whose contacts are being searched.
    :type user: User
    :param first_name: The first name to search for. Default is None.
    :type first_name: Optional[str]
    :param second_name: The last name to search for. Default is None.
    :type second_name: Optional[str]
    :param email: The email to search for. Default is None.
    :type email: Optional[str]
    :return: A list of contacts matching the search criteria.
    :rtype: List[Contact]
    """
    query = db.query(Contact).filter(Contact.user_id == user.id)
    if first_name:
        query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
    if second_name:
        query = query.filter(Contact.second_name.ilike(f"%{second_name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))
    return query.all()


def get_upcoming_birthdays(db: Session, user: User) -> List[Contact]:
    """
    Retrieves contacts with upcoming birthdays within the next 7 days.

    :param db: The database session.
    :type db: Session
    :param user: The user whose contacts are being checked.
    :type user: User
    :return: A list of contacts with upcoming birthdays.
    :rtype: List[Contact]
    """
    today = date.today()
    seven_days_later = today + timedelta(days=7)
    contacts_with_upcoming_birthdays = db.query(Contact).filter(
        Contact.user_id == user.id,
        extract('month', cast(Contact.birthdate, Date)) == today.month,
        extract('day', cast(Contact.birthdate, Date)) >= today.day,
        extract('day', cast(Contact.birthdate, Date)) <= seven_days_later.day
    ).all()
    if today.month != seven_days_later.month:
        contacts_with_upcoming_birthdays += db.query(Contact).filter(
            extract('month', cast(Contact.birthdate, Date)) == seven_days_later.month,
            extract('day', cast(Contact.birthdate, Date)) <= seven_days_later.day
        ).all()
    return contacts_with_upcoming_birthdays
