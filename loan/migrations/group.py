from django.db import migrations
from django.contrib.auth.models import Group, Permission


def create_agent_group_and_permissions(apps, schema_editor):
    """
    Creates agent group along with required permissions
    """

    group = Group.objects.create(name="Agent")

    customer_permissions = Permission.objects.filter(
        content_type__model="customerprofile"
    )
    loan_permissions = Permission.objects.filter(
        content_type__model="loan"
    )

    for permission in customer_permissions:
        group.permissions.add(permission)

    for permission in loan_permissions:
        group.permissions.add(permission)


class Migration(migrations.Migration):

    dependencies = [
        ('loan', '0003_alter_loan_loan_type'),
    ]

    operations = [
        migrations.RunPython(create_agent_group_and_permissions)
    ]