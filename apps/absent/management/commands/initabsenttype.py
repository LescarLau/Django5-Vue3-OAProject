from django.core.management.base import BaseCommand
from apps.absent.models import AbsentType

class Command(BaseCommand):
    def handle(self, *args, **options):
        absent_types = ['事假','病假','工伤假','婚夹','丧假','产假','探亲假','公假','年休假']
        absents = []
        for absent_type in absent_types:
            absents.append(AbsentType(name=absent_type))
        AbsentType.objects.bulk_create(absents)
        self.stdout.write('考勤类型初始化成功')
