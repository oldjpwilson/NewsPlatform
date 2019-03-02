# Generated by Django 2.1.5 on 2019-03-02 18:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20190302_1741'),
    ]

    operations = [
        migrations.CreateModel(
            name='Charge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('stripe_charge_id', models.CharField(blank=True, max_length=50, null=True)),
                ('success', models.BooleanField(default=True)),
                ('profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Profile')),
            ],
        ),
        migrations.RemoveField(
            model_name='channel',
            name='stripe_plan_id',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='stripe_subscription_id',
        ),
        migrations.AddField(
            model_name='payout',
            name='stripe_transfer_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='channel',
            name='stripe_account_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='payout',
            name='channel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Channel'),
        ),
    ]
