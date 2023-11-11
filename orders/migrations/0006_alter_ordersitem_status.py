# Generated by Django 4.2.6 on 2023-11-09 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_alter_ordersitem_status_cancelledorderitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordersitem',
            name='status',
            field=models.CharField(choices=[('Order confirmed', 'Order confirmed'), ('Shipped', 'Shipped'), ('Out for delivery', 'Out for delivery'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled'), ('Cancell request send', 'Cancell request send')], default='Order confirmed', max_length=255),
        ),
    ]
