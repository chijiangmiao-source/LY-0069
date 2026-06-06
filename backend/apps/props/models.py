from django.db import models


class Prop(models.Model):
    STATUS_CHOICES = (
        ('in_store', '在库'),
        ('loaded', '已装车'),
        ('damaged', '损坏'),
        ('lost', '丢失'),
    )

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='道具编号'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='道具名称'
    )
    program_id = models.ForeignKey(
        'programs.Program',
        on_delete=models.CASCADE,
        related_name='props',
        verbose_name='所属剧目'
    )
    material = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='材质'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_store',
        verbose_name='当前状态'
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='存放位置'
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
        verbose_name = '道具'
        verbose_name_plural = '道具'
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.code}] {self.name}'
