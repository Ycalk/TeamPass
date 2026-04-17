from .admin import AdminView
from .change_password import ChangePasswordView
from .student import StudentView
from .student_import import StudentImportView
from .user import UserView

__all__ = [
    "AdminView",
    "ChangePasswordView",
    "StudentView",
    "UserView",
    "StudentImportView",
]
