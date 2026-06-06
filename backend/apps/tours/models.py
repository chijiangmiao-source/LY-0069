from django.db import models
from django.core.exceptions import ValidationError
from datetime import date


class TourTask(models.Model):
    STATUS_CHOICES = (
        ('pending', '待执行'),
        ('in_progress', '执行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
        ('abnormal', '异常'),
    )

    EXECUTION_STATUS_CHOICES = (
        ('not_started', '未开始'),
        ('preparing', '筹备中'),
        ('transporting', '运输中'),
        ('performing', '演出中'),
        ('returning', '返程中'),
        ('finished', '已结束'),
    )

    program = models.ForeignKey(
        'programs.Program',
        on_delete=models.CASCADE,
        related_name='tour_tasks',
        verbose_name='剧目'
    )
    performance_date = models.DateField(
        verbose_name='演出日期'
    )
    city = models.CharField(
        max_length=100,
        verbose_name='演出城市'
    )
    venue = models.CharField(
        max_length=200,
        verbose_name='场馆'
    )
    person_in_charge = models.CharField(
        max_length=100,
        verbose_name='负责人'
    )
    start_date = models.DateField(
        verbose_name='任务开始日期'
    )
    end_date = models.DateField(
        verbose_name='任务结束日期'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='任务状态'
    )
    execution_status = models.CharField(
        max_length=20,
        choices=EXECUTION_STATUS_CHOICES,
        default='not_started',
        verbose_name='执行状态'
    )
    abnormal_situation = models.TextField(
        blank=True,
        null=True,
        verbose_name='异常情况'
    )
    completion_result = models.TextField(
        blank=True,
        null=True,
        verbose_name='完成结果'
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
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        verbose_name = '巡演任务'
        verbose_name_plural = '巡演任务'
        ordering = ['-performance_date']

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError({'start_date': '任务开始日期不能晚于结束日期'})
        if self.performance_date < self.start_date or self.performance_date > self.end_date:
            raise ValidationError({'performance_date': '演出日期必须在任务开始和结束日期之间'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.program.name} - {self.city} - {self.performance_date}'


class TourTaskVehicle(models.Model):
    tour_task = models.ForeignKey(
        TourTask,
        on_delete=models.CASCADE,
        related_name='task_vehicles',
        verbose_name='巡演任务'
    )
    vehicle = models.ForeignKey(
        'vehicles.Vehicle',
        on_delete=models.CASCADE,
        related_name='tour_assignments',
        verbose_name='车辆'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        verbose_name = '任务车辆'
        verbose_name_plural = '任务车辆'
        unique_together = [['tour_task', 'vehicle']]

    def __str__(self):
        return f'{self.tour_task} - {self.vehicle.code}'


class TourTaskProp(models.Model):
    tour_task = models.ForeignKey(
        TourTask,
        on_delete=models.CASCADE,
        related_name='task_props',
        verbose_name='巡演任务'
    )
    prop = models.ForeignKey(
        'props.Prop',
        on_delete=models.CASCADE,
        related_name='tour_assignments',
        verbose_name='道具'
    )
    quantity = models.IntegerField(
        default=1,
        verbose_name='数量'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        verbose_name = '任务道具'
        verbose_name_plural = '任务道具'
        unique_together = [['tour_task', 'prop']]

    def __str__(self):
        return f'{self.tour_task} - {self.prop.code}'
