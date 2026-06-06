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


class TourCostItem(models.Model):
    COST_TYPE_CHOICES = (
        ('transport', '运输费'),
        ('labor', '人工费'),
        ('venue', '场地费'),
        ('maintenance', '维保费'),
        ('temporary_purchase', '临时采购费'),
        ('abnormal_handling', '异常处理费'),
    )

    tour_task = models.ForeignKey(
        TourTask,
        on_delete=models.CASCADE,
        related_name='cost_items',
        verbose_name='巡演任务'
    )
    cost_type = models.CharField(
        max_length=30,
        choices=COST_TYPE_CHOICES,
        verbose_name='费用类型'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='金额'
    )
    description = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='费用说明'
    )
    expense_date = models.DateField(
        verbose_name='费用发生日期'
    )
    operator = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='经办人'
    )
    receipt_no = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='票据编号'
    )
    is_abnormal_cost = models.BooleanField(
        default=False,
        verbose_name='是否为异常费用'
    )
    abnormal_remark = models.TextField(
        blank=True,
        null=True,
        verbose_name='异常费用说明'
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
        verbose_name = '巡演成本项'
        verbose_name_plural = '巡演成本项'
        ordering = ['-expense_date']

    def clean(self):
        if self.amount < 0:
            raise ValidationError({'amount': '金额不能为负数'})
        if self.tour_task_id:
            task = TourTask.objects.filter(id=self.tour_task_id).first()
            if task:
                if self.expense_date < task.start_date or self.expense_date > task.end_date:
                    raise ValidationError({'expense_date': '费用发生日期必须在任务开始和结束日期之间'})

    def save(self, *args, **kwargs):
        if self.cost_type == 'abnormal_handling':
            self.is_abnormal_cost = True
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.tour_task} - {self.get_cost_type_display()} - ¥{self.amount}'


class TourSettlement(models.Model):
    SETTLEMENT_STATUS_CHOICES = (
        ('draft', '草稿'),
        ('submitted', '已提交'),
        ('confirmed', '已确认'),
    )

    tour_task = models.OneToOneField(
        TourTask,
        on_delete=models.CASCADE,
        related_name='settlement',
        verbose_name='巡演任务'
    )
    settlement_no = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='结算单号'
    )
    transport_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='运输费合计'
    )
    labor_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='人工费合计'
    )
    venue_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='场地费合计'
    )
    maintenance_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='维保费合计'
    )
    temporary_purchase_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='临时采购费合计'
    )
    abnormal_handling_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='异常处理费合计'
    )
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='总成本'
    )
    abnormal_cost_note = models.TextField(
        blank=True,
        null=True,
        verbose_name='异常费用说明'
    )
    settlement_status = models.CharField(
        max_length=20,
        choices=SETTLEMENT_STATUS_CHOICES,
        default='draft',
        verbose_name='结算状态'
    )
    settler = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='结算人'
    )
    settlement_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='结算日期'
    )
    remark = models.TextField(
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
        verbose_name = '巡演结算单'
        verbose_name_plural = '巡演结算单'
        ordering = ['-created_at']

    def calculate_total(self):
        self.total_cost = (
            self.transport_cost + self.labor_cost + self.venue_cost +
            self.maintenance_cost + self.temporary_purchase_cost + self.abnormal_handling_cost
        )
        return self.total_cost

    def aggregate_from_cost_items(self):
        from django.db.models import Sum
        items = self.tour_task.cost_items.all()
        agg = items.values('cost_type').annotate(total=Sum('amount'))
        cost_map = {item['cost_type']: float(item['total']) for item in agg}
        self.transport_cost = cost_map.get('transport', 0)
        self.labor_cost = cost_map.get('labor', 0)
        self.venue_cost = cost_map.get('venue', 0)
        self.maintenance_cost = cost_map.get('maintenance', 0)
        self.temporary_purchase_cost = cost_map.get('temporary_purchase', 0)
        self.abnormal_handling_cost = cost_map.get('abnormal_handling', 0)
        self.calculate_total()

    def __str__(self):
        return f'{self.settlement_no} - {self.tour_task}'
