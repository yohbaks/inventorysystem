import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventorysystem.settings')
django.setup()

from django.contrib.auth.models import User
from inventory.models import Notification

user = User.objects.first()

Notification.objects.create(user=user, notification_type='pm_overdue', title='URGENT: PM Overdue', message='Desktop PC-001 is overdue', priority='urgent')
Notification.objects.create(user=user, notification_type='pm_due', title='PM Due Soon', message='Desktop PC-005 needs maintenance', priority='high')
Notification.objects.create(user=user, notification_type='asset_added', title='New Asset', message='Laptop LT-001 added', priority='normal')
Notification.objects.create(user=user, notification_type='employee_added', title='New Employee', message='John Doe added', priority='low')
Notification.objects.create(user=user, notification_type='system', title='System Update', message='Updated to v3.0', priority='low')

print(f"Created {Notification.objects.count()} notifications!")