from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0004_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='is_all_day',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='event',
            name='start_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='end_time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
