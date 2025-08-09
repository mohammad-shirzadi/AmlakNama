from django.core.management import BaseCommand
from django.db import transaction
from django_celery_beat.models import CrontabSchedule, PeriodicTask,IntervalSchedule
from tasks.tasks import updatedata as updatedata_task
from django.utils.timezone import get_default_timezone_name


class Command(BaseCommand):
    help = """
    Setup celery beat periodic tasks.

    Following tasks will be created:

        - update the datas
    """

    @transaction.atomic
    def handle(self, *args, **kwargs):
        print('Deleting all periodic tasks and schedules...\n')

        CrontabSchedule.objects.all().delete()
        PeriodicTask.objects.all().delete()
        IntervalSchedule.objects.all().delete()


        """
        Example:
        {
            'task': periodic_task_name,
            'name': 'Periodic task description',
            # Everyday at 15:45
            # https://crontab.guru/#45_15_*_*_*
            'cron': {
                'minute': '45',
                'hour': '15',
                'day_of_week': '*',
                'day_of_month': '*',
                'month_of_year': '*',
            },
            'enabled': True
        },
        """
        
        periodic_tasks =[
            {
                'task':updatedata_task,
                'name':'update the datas',
                'cron':{
                    'minute':'0',
                    'hour':'0,2,4,6,8,10,12,14,16,18,20,22',
                    'day_of_month':'*',
                    'month_of_year':'*',
                    'day_of_week':'*',
                }
            }
        ]

        timezone = get_default_timezone_name()

        for task in periodic_tasks:
            cron = CrontabSchedule.objects.create(
                timezone=timezone,
                **task['cron']
                )
            PeriodicTask.objects.create(
                name=task['name'],
                task=task['task'].name,
                crontab=cron
                )

        