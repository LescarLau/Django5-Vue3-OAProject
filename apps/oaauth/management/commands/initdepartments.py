from django.core.management.base import BaseCommand
from apps.oaauth.models import OADepartment


class Command(BaseCommand):
    def handle(self, *args, **options):
        # 初始化部门数据
        boarder = OADepartment.objects.create(name='董事会', intro="董事会")
        developer = OADepartment.objects.create(name='产品开发部', intro="产品设计，技术开发")
        operator = OADepartment.objects.create(name='运营部', intro="客户运营，产品运营")
        saler = OADepartment.objects.create(name='销售部', intro="销售产品")
        hr = OADepartment.objects.create(name='人事部', intro="员工招聘，员工培训，员工考核")
        finance = OADepartment.objects.create(name='财务部', intro="财务报表，财务审核")
        self.stdout.write('部门数据初始化成功！')