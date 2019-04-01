from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, phone, nickname, password=None):
        if not phone:
            raise ValueError('Users must have a phone number')

        user = self.model(
            phone=phone,
            nickname=nickname,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, nickname, password):
        user = self.create_user(phone,
            nickname,
            password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    phone = models.CharField(verbose_name='phone', unique=True, max_length=11)
    nickname = models.CharField(unique=True, max_length=30)
    password = models.CharField(max_length=128)
    email = models.EmailField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    def __str__(self):
        if len(self.nickname) > 10:
            return self.nickname[:10]+"..."
        return self.nickname

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    class Meta:
        db_table = 'user'


class Msg_send_log(models.Model):
    phone = models.CharField(verbose_name='phone', max_length=11)
    msg_code = models.CharField(max_length=6)
    send_time = models.DateTimeField(auto_now_add=True)
    verify_times = models.IntegerField(default=0)
    def __str__(self):
        return self.phone
    class Meta:
        db_table = 'msg_send_log'

class Email_send_log(models.Model):
    phone = models.CharField(verbose_name="phone", max_length=11)
    email = models.EmailField(max_length=255)
    token = models.CharField(max_length=24)
    send_time = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)
    def __str__(self):
        return self.phone
    class Meta:
        db_table = 'email_send_log'
            
        