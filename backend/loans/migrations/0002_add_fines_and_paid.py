
from django.db import migrations, models
import decimal


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='loan',
            name='fine_amount',
            field=models.DecimalField(default=decimal.Decimal('0.00'), max_digits=10, decimal_places=2, verbose_name='Multa'),
        ),
        migrations.AddField(
            model_name='loan',
            name='fine_last_updated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Última atualização da multa'),
        ),
        migrations.AddField(
            model_name='loan',
            name='paid',
            field=models.BooleanField(default=False, verbose_name='Multa Paga'),
        ),
        migrations.AddField(
            model_name='loan',
            name='paid_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Data do Pagamento'),
        ),
    ]
