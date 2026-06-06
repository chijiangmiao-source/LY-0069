from django.db import models
from datetime import timedelta


class Prop(models.Model):
    STATUS_CHOICES = (
        ('in_store', '在库'),
        ('loaded', '已装车'),
        ('damaged', '损坏'),
        ('lost', '丢失'),
        ('scrapped', '已报废'),
    )

    MAINTENANCE_STATUS_CHOICES = (
        ('normal', '正常'),
        ('pending', '待维保'),
        ('overdue', '超期未维保'),
        ('in_maintenance', '维保中'),
    )

    SCRAP_STATUS_CHOICES = (
        ('active', '在用'),
        ('pending', '待审批'),
        ('approved', '已批准'),
        ('rejected', '已驳回'),
        ('scrapped', '已报废'),
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
    maintenance_cycle_days = models.IntegerField(
        default=90,
        verbose_name='维保周期(天)'
    )
    last_maintenance_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='最近维保时间'
    )
    next_maintenance_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='下次维保时间'
    )
    maintenance_status = models.CharField(
        max_length=20,
        choices=MAINTENANCE_STATUS_CHOICES,
        default='normal',
        verbose_name='维保状态'
    )
    scrap_status = models.CharField(
        max_length=20,
        choices=SCRAP_STATUS_CHOICES,
        default='active',
        verbose_name='报废状态'
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

    def save(self, *args, **kwargs):
        if self.last_maintenance_date and self.maintenance_cycle_days:
            self.next_maintenance_date = self.last_maintenance_date + timedelta(days=self.maintenance_cycle_days)
        super().save(*args, **kwargs)


class MaintenanceRecord(models.Model):
    TYPE_CHOICES = (
        ('repair', '维修'),
        ('maintenance', '保养'),
        ('inspection', '复检'),
    )

    RESULT_CHOICES = (
        ('pass', '合格'),
        ('fail', '不合格'),
        ('pending', '待确认'),
    )

    prop = models.ForeignKey(
        Prop,
        on_delete=models.CASCADE,
        related_name='maintenance_records',
        verbose_name='道具'
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name='维保类型'
    )
    maintenance_date = models.DateField(
        verbose_name='维保日期'
    )
    description = models.TextField(
        verbose_name='维保描述'
    )
    operator = models.CharField(
        max_length=100,
        verbose_name='操作人'
    )
    result = models.CharField(
        max_length=20,
        choices=RESULT_CHOICES,
        default='pending',
        verbose_name='维保结果'
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='费用'
    )
    remark = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='备注'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        verbose_name = '维保记录'
        verbose_name_plural = '维保记录'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_type_display()}-{self.prop.code}'


class ScrapApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', '待审批'),
        ('approved', '已批准'),
        ('rejected', '已驳回'),
        ('cancelled', '已取消'),
    )

    prop = models.ForeignKey(
        Prop,
        on_delete=models.CASCADE,
        related_name='scrap_applications',
        verbose_name='道具'
    )
    applicant = models.CharField(
        max_length=100,
        verbose_name='申请人'
    )
    apply_date = models.DateField(
        verbose_name='申请日期'
    )
    reason = models.TextField(
        verbose_name='报废原因'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='审批状态'
    )
    approver = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='审批人'
    )
    approve_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='审批日期'
    )
    approve_remark = models.TextField(
        blank=True,
        null=True,
        verbose_name='审批意见'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        verbose_name = '报废申请'
        verbose_name_plural = '报废申请'
        ordering = ['-created_at']

    def __str__(self):
        return f'报废申请-{self.prop.code}'
