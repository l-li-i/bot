import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auction_app', '0002_initial'),
        ('support_app', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='complaint',
            name='reporter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reported_complaints', to=settings.AUTH_USER_MODEL, verbose_name='Подавший жалобу'),
        ),
        migrations.AddField(
            model_name='complaint',
            name='resolved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='resolved_complaints', to=settings.AUTH_USER_MODEL, verbose_name='Решена'),
        ),
        migrations.AddField(
            model_name='complaint',
            name='target_admin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_complaints', to=settings.AUTH_USER_MODEL, verbose_name='Администратор, на которого жалуются'),
        ),
        migrations.AddField(
            model_name='lotapproval',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Одобрено'),
        ),
        migrations.AddField(
            model_name='lotapproval',
            name='lot',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='approval_status', to='auction_app.lot', verbose_name='Лот'),
        ),
    ]
