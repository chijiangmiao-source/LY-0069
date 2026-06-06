from django.db import models


class Program(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='剧目名称'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='描述'
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
        verbose_name = '剧目'
        verbose_name_plural = '剧目'
        ordering = ['-created_at']

    def __str__(self):
        return self.name
