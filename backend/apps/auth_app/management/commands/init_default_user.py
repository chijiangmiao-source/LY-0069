from django.core.management.base import BaseCommand
from apps.auth_app.models import User


class Command(BaseCommand):
    help = '创建默认测试用户 (admin/admin123)'

    def handle(self, *args, **options):
        username = 'admin'
        password = 'admin123'

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'用户 {username} 已存在'))
        else:
            User.objects.create_superuser(
                username=username,
                password=password,
                email='admin@example.com',
                role='admin'
            )
            self.stdout.write(self.style.SUCCESS(f'成功创建管理员用户: {username} / {password}'))

        staff_username = 'staff'
        staff_password = 'staff123'
        if User.objects.filter(username=staff_username).exists():
            self.stdout.write(self.style.WARNING(f'用户 {staff_username} 已存在'))
        else:
            User.objects.create_user(
                username=staff_username,
                password=staff_password,
                email='staff@example.com',
                role='staff'
            )
            self.stdout.write(self.style.SUCCESS(f'成功创建普通用户: {staff_username} / {staff_password}'))
