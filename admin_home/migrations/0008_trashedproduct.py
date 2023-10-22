# Generated by Django 4.2.6 on 2023-10-21 15:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admin_home', '0007_rename_side_image_1_productimage_image_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrashedProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('discount_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Unisex', 'Unisex')], default='Unisex', max_length=10)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_home.category')),
                ('images', models.ManyToManyField(to='admin_home.productimage')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_home.product')),
                ('size_variants', models.ManyToManyField(to='admin_home.sizevariant')),
            ],
        ),
    ]
