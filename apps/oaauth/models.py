from django.db import models
from django.contrib.auth.models import User,PermissionsMixin,UserManager
from django.contrib.auth.base_user import AbstractBaseUser,BaseUserManager
from django.contrib.auth.hashers import make_password
from shortuuidfield import ShortUUIDField

# Create your models here.

class UserStatusChoice(models.IntegerChoices):
    # 已经激活
    ACTIVED = 1
    # 未激活
    UNACTIVE = 2
    # 锁定
    LOCKED = 3

# 重写UserManager
class OAUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, realname, email, password, **extra_fields):
        """
        创建用户.
        """
        if not realname:
            raise ValueError("必须设置真实姓名")
        email = self.normalize_email(email)
        # 这里self.model为OAUSer，后续谁调用该Manager就会为当前model，这样写兼容性更好
        user = self.model(realname=realname, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, realname, email=None, password=None, **extra_fields):
        # 创建普通用户
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(realname, email, password, **extra_fields)

    def create_superuser(self, realname, email=None, password=None, **extra_fields):
        # 创建超级用户
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault('status',UserStatusChoice.ACTIVED)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("超级用户必须设置is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("超级用户必须设置is_superuser=True.")

        return self._create_user(realname, email, password, **extra_fields)


# 重写User模型
class OAUser(AbstractBaseUser, PermissionsMixin):
    """
    自定义的User模型
    """
    uid = ShortUUIDField(primary_key=True)
    realname = models.CharField( max_length=150, unique=False )
    email = models.EmailField(unique=True, blank=True)
    telephone = models.CharField(max_length=20,blank=True,)  # unique=True)
    is_staff = models.BooleanField(default=True)
    status = models.IntegerField(choices=UserStatusChoice,default=UserStatusChoice.UNACTIVE)
    # 只需要关注status，无需关注is_active
    is_active = models.BooleanField(default=True)  
    date_joined = models.DateTimeField(auto_now=True)

    department = models.ForeignKey('OADepartment',null=True,on_delete=models.SET_NULL,related_name='staffs',related_query_name='staffs')

    objects = OAUserManager()

    EMAIL_FIELD = "email"
    # USERNAME_FIELD是用来做鉴权的，会把authencate的username参数，传给USERNAME_FIELD指定的字段
    from django.contrib.auth import authenticate
    USERNAME_FIELD = "email"
    # REQUIRED_FIELDS指定哪些字段是必须要传的，但不能重复包含USERNAME_FIELD和EMAIL_FIELD已经设置的值
    REQUIRED_FIELDS = ["realname","password"]

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        # """
        # Return the first_name plus the last_name, with a space in between.
        # """
        # full_name = "%s %s" % (self.first_name, self.last_name)
        # return full_name.strip()
        return self.realname

    def get_short_name(self):
        """Return the short name for the user."""
        return self.realname


class OADepartment(models.Model):
    name = models.CharField(max_length=100)
    intro = models.CharField(max_length=200)
    # leader
    leader = models.OneToOneField(OAUser,null=True,on_delete=models.SET_NULL,related_name='leader_department',related_query_name='leader_department')
    # manager
    manager = models.ForeignKey(OAUser,null=True,on_delete=models.SET_NULL,related_name='manager_department',related_query_name='manager_department')
