from django.contrib.auth import get_user_model
from django.test import TestCase
from users.errors import (
    InvalidCredentialsError,
    PermissionDeniedError,
    UserAlreadyExistsError,
    UserDeactivatedError,
    UserNotFoundError,
    UserRecoveryError,
)
from users.services import UserService

User = get_user_model()
DEFAULT_PASSWORD = "password#123"  # noqa: S105
WRONG_PASSWORD = "wrongone"  # noqa: S105


class UserServiceTests(TestCase):
    def setUp(self):
        self.service = UserService()
        self.user_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password": DEFAULT_PASSWORD,
        }
        self.user = self.service.register(self.user_data)

    def test_register(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertTrue(User.all_with_deleted.filter(username="testuser").exists())

    def test_authenticate(self):
        auth_data = {"username": "testuser", "password": DEFAULT_PASSWORD}
        result = self.service.authenticate_user(auth_data)
        self.assertIn("access", result)
        self.assertEqual(result["user"], self.user)

    def test_update_profile(self):
        updated = self.service.update_profile(
            self.user.id,
            {"first_name": "newname"},
            self.user,
        )
        self.assertEqual(updated.first_name, "newname")

    def test_deactivate_account(self):
        self.service.deactivate_account(self.user.id, self.user)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

        deactivated_user = User.all_with_deleted.get(id=self.user.id)
        self.assertIsNotNone(deactivated_user.deleted_at)
        self.assertFalse(deactivated_user.is_active)

    def test_recover_account(self):
        self.service.deactivate_account(self.user.id, self.user)
        recovered = self.service.recover_account(self.user.email)
        self.assertIsNone(recovered.deleted_at)
        self.assertTrue(User.objects.filter(id=self.user.id).exists())

    def test_authenticate_invalid_error(self):
        with self.assertRaises(InvalidCredentialsError):
            self.service.authenticate_user(
                {"username": "testuser", "password": WRONG_PASSWORD}
            )

    def test_register_duplicate_error(self):
        with self.assertRaises(UserAlreadyExistsError):
            self.service.register(self.user_data)

    def test_get_profile_not_found_error(self):
        with self.assertRaises(UserNotFoundError):
            self.service.get_profile(999999)

    def test_authenticate_deactivated_error(self):
        self.service.deactivate_account(self.user.id, self.user)
        with self.assertRaises(UserDeactivatedError):
            self.service.authenticate_user(
                {"username": "testuser", "password": DEFAULT_PASSWORD}
            )

    def test_update_deactivated_profile_error(self):
        self.service.deactivate_account(self.user.id, self.user)
        with self.assertRaises(UserDeactivatedError):
            self.service.update_profile(
                self.user.id,
                {"first_name": "newname"},
                self.user,
            )

    def test_recover_active_error(self):
        with self.assertRaises(UserRecoveryError):
            self.service.recover_account(self.user.email)

    def test_recover_non_existing_user_error(self):
        with self.assertRaises(UserRecoveryError):
            self.service.recover_account("notexist@test.com")

    def test_update_wrong_profile_error(self):
        other_user = User.objects.create_user(
            username="other",
            password=DEFAULT_PASSWORD,
        )
        with self.assertRaises(PermissionDeniedError):
            self.service.update_profile(
                self.user.id,
                {"first_name": "hisnewname"},
                other_user,
            )
