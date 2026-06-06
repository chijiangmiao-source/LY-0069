from django.db import models


class LoadingRecord(models.Model):
    vehicle = models.ForeignKey(
        'vehicles.Vehicle',
        on_delete=models.CASCADE,
        related_name='loading_records',
        verbose_name='车辆'
    )
    prop = models.ForeignKey(
        'props.Prop',
        on_delete=models.CASCADE,
        related_name='loading_records',
        verbose_name='道具'
    )
    loading_date = models.DateField(
        verbose_name='装车日期'
    )
    loading_quantity = models.IntegerField(
        default=1,
        verbose_name='装车数量'
    )
    operator = models.CharField(
        max_length=100,
        verbose_name='操作人'
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
        verbose_name = '装车登记'
        verbose_name_plural = '装车登记'
        ordering = ['-created_at']

    def __str__(self):
        return f'装车-{self.vehicle.code}-{self.prop.code}'


class UnloadingRecord(models.Model):
    loading = models.OneToOneField(
        LoadingRecord,
        on_delete=models.CASCADE,
        related_name='unloading_record',
        verbose_name='装车记录'
    )
    vehicle = models.ForeignKey(
        'vehicles.Vehicle',
        on_delete=models.CASCADE,
        related_name='unloading_records',
        verbose_name='车辆'
    )
    prop = models.ForeignKey(
        'props.Prop',
        on_delete=models.CASCADE,
        related_name='unloading_records',
        verbose_name='道具'
    )
    unloading_date = models.DateField(
        verbose_name='卸车日期'
    )
    unloading_quantity = models.IntegerField(
        verbose_name='卸车数量'
    )
    operator = models.CharField(
        max_length=100,
        verbose_name='操作人'
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
        verbose_name = '卸车归库'
        verbose_name_plural = '卸车归库'
        ordering = ['-created_at']

    def __str__(self):
        return f'卸车-{self.vehicle.code}-{self.prop.code}'


class DamageRecord(models.Model):
    prop = models.ForeignKey(
        'props.Prop',
        on_delete=models.CASCADE,
        related_name='damage_records',
        verbose_name='道具'
    )
    damage_date = models.DateField(
        verbose_name='损耗日期'
    )
    damage_quantity = models.IntegerField(
        verbose_name='损耗数量'
    )
    damage_reason = models.CharField(
        max_length=500,
        verbose_name='损耗原因'
    )
    handler = models.CharField(
        max_length=100,
        verbose_name='处理人'
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
        verbose_name = '损耗记录'
        verbose_name_plural = '损耗记录'
        ordering = ['-created_at']

    def __str__(self):
        return f'损耗-{self.prop.code}'
