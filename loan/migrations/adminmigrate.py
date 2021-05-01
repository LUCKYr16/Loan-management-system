from django.db import migrations
from django.contrib.auth import get_user_model


class Migration(migrations.Migration):

    def generate_superuser(apps, schema_editor):
        User = get_user_model()

        superuser = User.objects.create_superuser(
            username="internadmin",
            email="admin@example.com",
            password="admin")

        superuser.save()

    operations = [
        migrations.RunPython(generate_superuser),
    ]

    dependencies = [
        ('loan', 'group'),
    ]