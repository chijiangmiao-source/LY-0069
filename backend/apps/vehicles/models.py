from django.db import models
from django.core.exceptions import ValidationError


class Vehicle(models.Model):
    STATUS_CHOICES = (
        ('active', '启用'),
        ('inactive', '停用'),
    )

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='车辆编号'
    )
    model = models.CharField(
        max_length=100,
        verbose_name='车型'
    )
    capacity = models.IntegerField(
        verbose_name='承载容量'
    )
    current_load = models.IntegerField(
        default=0,
        verbose_name='当前装载量'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='车辆状态'
    )
    driver = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='责任司机'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        verbose_name = '车辆'
        verbose_name_plural = '车辆'

    def clean(self):
        if self.current_load > self.capacity:
            raise ValidationError({'current_load': '当前装载量不能超过承载容量'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.code} - {self.model}'
