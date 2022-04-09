from lib2to3.pytree import Base
from tabnanny import verbose
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migration = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get('is_staff') is False:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is False:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(
        _("email address"),
        blank=False,
        null=True,
        unique=True)
    is_owner = models.BooleanField(default=False, null=False, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        return self.email


class Shop(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, blank=False)
    shop_name = models.CharField(
        max_length=255,null=False, blank=False)
    shop_location = models.CharField(
        max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return self.shop_name
