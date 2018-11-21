from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings

class AccountManager(BaseUserManager):
        def create_user(self, email, first_name, last_name, password=None):
            if not email:
                raise ValueError('Users must have an email address')
            if not first_name:
                raise ValueError('Users must have an first name')
            if not last_name:
                raise ValueError('Users must have an last name')
            user = self.model(
            email=self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            )

            user.set_password(password)
            user.save(using=self._db)
            return user

        def create_superuser(self, email, first_name, last_name, password):
            user = self.create_user(
                email,
                password=password,
                first_name = first_name,
                last_name = last_name,
            )
            user.is_admin = True
            user.save(using=self._db)
            return user

class Account(AbstractBaseUser):
        email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
        first_name = models.CharField(max_length=40, blank=True)
        last_name = models.CharField(max_length=40, blank=True)
        is_admin = models.BooleanField(default=False)
        is_active = models.BooleanField(default=True)

        objects = AccountManager()

        USERNAME_FIELD = 'email'
        REQUIRED_FIELDS = ['first_name', 'last_name']

        def has_perm(self, perm, obj=None):
            "Does the user have a specific permission?"
            # Simplest possible answer: Yes, always
            return True

        def has_module_perms(self, app_label):
            "Does the user have permissions to view the app `app_label`?"
            # Simplest possible answer: Yes, always
            return True

        @property
        def is_staff(self):
            "Is the user a member of staff?"
            # Simplest possible answer: All admins are staff
            return self.is_admin

        def get_full_name(self):
            return '{} {}'.format(self.first_name, self.last_name)

class Profile(models.Model):
        account = models.OneToOneField(
            settings.AUTH_USER_MODEL,
            on_delete = models.CASCADE,
            primary_key = True,
            related_name = 'account_of',
        )
        friends = models.ManyToManyField(
            'self',
            related_name = 'friends_of'
        )

        def user_toJSON(self):
            return {
                'id': self.account.id,
                'label': self.account.first_name
            }

        def friend_toJSON(self, friend):
            return {
                    'from': self.account.id,
                    'to': friend.account.id
            }

class Friend_Request(models.Model):
    sender = models.ForiegnKey(
            settings.AUTH_USER_MODEL,
            on_delete = models.CASCADE,
            related_name = 'sender_notification',
        )

    receiver = models.ForiegnKey(
            settings.AUTH_USER_MODEL,
            on_delete = models.CASCADE,
            related_name = 'receiver_notification',
        )

    PENDING = 'PE'
    ACCEPTED = 'AC'
    DECLINED = 'DE'
    STATUS_OF_REQUEST_CHOICES = (
            (PENDING, 'pending'),
            (ACCEPTED, 'accepted'),
            (DECLINED, 'declined'),
        )

    status = models.CharField(
        max_length = 2,
        choices = STATUS_OF_REQUEST_CHOICES,
        default = PENDING,
        )

    created_or_updated_at = models.DateTimeField()
    sender_read = models.BooleanField(default=True)
    receiver_read = models.BooleanField(default=False)
