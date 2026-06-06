from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('programs', '0001_initial'),
        ('vehicles', '0001_initial'),
        ('props', '0002_prop_last_maintenance_date_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TourTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('performance_date', models.DateField(verbose_name='演出日期')),
                ('city', models.CharField(max_length=100, verbose_name='演出城市')),
                ('venue', models.CharField(max_length=200, verbose_name='场馆')),
                ('person_in_charge', models.CharField(max_length=100, verbose_name='负责人')),
                ('start_date', models.DateField(verbose_name='任务开始日期')),
                ('end_date', models.DateField(verbose_name='任务结束日期')),
                ('status', models.CharField(
                    choices=[
                        ('pending', '待执行'),
                        ('in_progress', '执行中'),
                        ('completed', '已完成'),
                        ('cancelled', '已取消'),
                        ('abnormal', '异常'),
                    ],
                    default='pending',
                    max_length=20,
                    verbose_name='任务状态'
                )),
                ('execution_status', models.CharField(
                    choices=[
                        ('not_started', '未开始'),
                        ('preparing', '筹备中'),
                        ('transporting', '运输中'),
                        ('performing', '演出中'),
                        ('returning', '返程中'),
                        ('finished', '已结束'),
                    ],
                    default='not_started',
                    max_length=20,
                    verbose_name='执行状态'
                )),
                ('abnormal_situation', models.TextField(blank=True, null=True, verbose_name='异常情况')),
                ('completion_result', models.TextField(blank=True, null=True, verbose_name='完成结果')),
                ('remark', models.CharField(blank=True, max_length=500, null=True, verbose_name='备注')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('program', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='tour_tasks',
                    to='programs.program',
                    verbose_name='剧目'
                )),
            ],
            options={
                'verbose_name': '巡演任务',
                'verbose_name_plural': '巡演任务',
                'ordering': ['-performance_date'],
            },
        ),
        migrations.CreateModel(
            name='TourTaskProp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1, verbose_name='数量')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('prop', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='tour_assignments',
                    to='props.prop',
                    verbose_name='道具'
                )),
                ('tour_task', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='task_props',
                    to='tours.tourtask',
                    verbose_name='巡演任务'
                )),
            ],
            options={
                'verbose_name': '任务道具',
                'verbose_name_plural': '任务道具',
                'unique_together': {('tour_task', 'prop')},
            },
        ),
        migrations.CreateModel(
            name='TourTaskVehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('tour_task', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='task_vehicles',
                    to='tours.tourtask',
                    verbose_name='巡演任务'
                )),
                ('vehicle', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='tour_assignments',
                    to='vehicles.vehicle',
                    verbose_name='车辆'
                )),
            ],
            options={
                'verbose_name': '任务车辆',
                'verbose_name_plural': '任务车辆',
                'unique_together': {('tour_task', 'vehicle')},
            },
        ),
    ]
