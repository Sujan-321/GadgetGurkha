# Generated by Django 4.2.7 on 2024-03-15 03:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appGurkha', '0007_alter_order_payment_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('Cash on Delivery', 'Cash on Delivery'), ('Khalti', 'Khalti')], default='Cash on Delivery', max_length=20),
        ),
    ]
