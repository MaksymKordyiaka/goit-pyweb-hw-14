import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from datetime import date
from db.models import Contact, User
from schemas import ContactCreate
from repository.contacts import (
    get_contacts,
    get_contact,
    create_contact,
    delete_contact,
    upgrade_contact,
    search_contacts,
    get_upcoming_birthdays,
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = get_contacts(user=self.user, skip=0, limit=10, db=self.session)
        self.assertEqual(result, contacts)

    def test_get_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    def test_create_contact(self):
        body = ContactCreate(first_name="John", second_name="Doe", email="john@example.com", phone="123456789",
                             birthdate=date(1990, 1, 1))
        result = create_contact(db=self.session, contact=body, user=self.user)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.second_name, body.second_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertTrue(hasattr(result, "id"))

    def test_delete_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = delete_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    def test_delete_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = delete_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    def test_upgrade_contact_found(self):
        body = ContactCreate(first_name="John", second_name="Smith", email="john@example.com", phone="987654321",
                             birthdate=date(1990, 1, 1))
        contact = Contact(first_name="John", second_name="Doe", email="john@example.com", phone="123456789",
                          birthdate=date(1990, 1, 1))
        self.session.query().filter().first.return_value = contact
        self.session.commit.return_value = None
        result = upgrade_contact(contact_id=1, contact=body, user=self.user, db=self.session)
        self.assertEqual(result.second_name, body.second_name)
        self.assertEqual(result.phone, body.phone)

    def test_upgrade_contact_not_found(self):
        body = ContactCreate(first_name="John", second_name="Doe", email="john@example.com", phone="123456789",
                             birthdate=date(1990, 1, 1))
        self.session.query().filter().first.return_value = None
        result = upgrade_contact(contact_id=1, contact=body, user=self.user, db=self.session)
        self.assertIsNone(result)

    def test_search_contacts(self):
        contacts = [Contact(first_name="John", second_name="Doe", email="john@example.com"),
                    Contact(first_name="Jane", second_name="Doe", email="jane@example.com")]

        self.session.query().filter().filter().all.return_value = [contacts[0]]
        result = search_contacts(user=self.user, first_name="John", db=self.session)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].first_name, "John")

    def test_get_upcoming_birthdays(self):
        contacts = [Contact(first_name="John", birthdate=date(1990, 1, 2)),
                    Contact(first_name="Jane", birthdate=date(1990, 1, 5))]
        self.session.query().filter().all.return_value = contacts
        result = get_upcoming_birthdays(user=self.user, db=self.session)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].first_name, "John")


if __name__ == '__main__':
    unittest.main()
