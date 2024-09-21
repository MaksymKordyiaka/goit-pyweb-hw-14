import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from db.models import User
from schemas import UserCreate
from repository.users import get_user_by_email, create_user, update_token, confirmed_email, update_avatar


class TestUserFunctions(unittest.TestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.email = "test@example.com"
        self.username = "testuser"
        self.user = User(email=self.email, password="password", refresh_token=None, confirmed=False,
                         avatar="old_avatar_url")
        self.user_create = UserCreate(email=self.email, password="password", username=self.username)
        self.new_user = User(email=self.email, password="password", avatar="gravatar_image_url")
        self.url = "new_avatar_url"
        self.token = "new_refresh_token"

    def test_get_user_by_email_found(self):
        self.session.query().filter().first.return_value = self.user
        result = get_user_by_email(self.email, self.session)
        self.assertEqual(result, self.user)

    def test_get_user_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = get_user_by_email(self.email, self.session)
        self.assertIsNone(result)

    @patch('libgravatar.Gravatar.get_image', return_value="gravatar_image_url")
    def test_create_user(self, mock_get_image):
        self.session.add = MagicMock()
        self.session.commit = MagicMock()
        self.session.refresh = MagicMock()

        user_data = UserCreate(email=self.email, password="password", username=self.username)
        result_user = User(email=self.email, password="password", refresh_token=None, confirmed=False,
                           avatar="gravatar_image_url")
        self.session.add.return_value = result_user
        self.session.commit.return_value = None
        self.session.refresh.return_value = None

        created_user = create_user(db=self.session, user=user_data)

        self.assertEqual(created_user.email, self.email)
        self.assertEqual(created_user.password, "password")
        self.assertEqual(created_user.username, self.username)
        self.assertIsNotNone(created_user.avatar)

    def test_update_token(self):
        self.session.add = MagicMock()
        self.session.commit = MagicMock()

        update_token(self.user, self.token, self.session)
        self.assertEqual(self.user.refresh_token, self.token)
        self.session.commit.assert_called_once()

    def test_confirmed_email(self):
        self.session.query().filter().first.return_value = self.user
        confirmed_email(self.email, self.session)
        self.assertTrue(self.user.confirmed)
        self.session.commit.assert_called_once()

    def test_update_avatar(self):
        self.session.query().filter().first.return_value = self.user
        result = update_avatar(self.email, self.url, self.session)
        self.assertEqual(result.avatar, self.url)
        self.session.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
