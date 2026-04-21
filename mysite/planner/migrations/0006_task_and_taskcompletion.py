from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0005_event_timeframe_fields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=160)),
                ('start_date', models.DateField()),
                ('due_date', models.DateField()),
                ('repeat_type', models.CharField(choices=[('one_time', 'One time'), ('daily', 'Daily'), ('every_n_days', 'Every N days'), ('every_n_months', 'Every N months')], default='one_time', max_length=20)),
                ('repeat_interval', models.PositiveIntegerField(default=1)),
                ('recurrence_count', models.PositiveIntegerField(default=0)),
                ('is_completed', models.BooleanField(default=False)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['due_date', 'created_at', 'pk'],
            },
        ),
        migrations.CreateModel(
            name='TaskCompletion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title_snapshot', models.CharField(max_length=160)),
                ('completed_due_date', models.DateField()),
                ('completed_at', models.DateTimeField(auto_now_add=True)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='completions', to='planner.task')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_completions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-completed_at', '-pk'],
            },
        ),
    ]
