from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', '管理员'),
        ('staff', '工作人员'),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='staff',
        verbose_name='角色'
    )

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.username
