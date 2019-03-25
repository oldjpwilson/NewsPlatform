# Generated by Django 2.1.5 on 2019-03-05 21:48

from django.db import migrations, models
import django.db.models.deletion
import tinymce.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('thumbnail', models.ImageField(upload_to='')),
                ('media_type', models.CharField(choices=[('Text and Video', 'Text and Video'), ('Text and Picture', 'Text and Picture'), ('Text, Picture and Video', 'Text, Picture and Video'), ('Text', 'Text'), ('Picture', 'Picture'), ('Video', 'Video')], max_length=40)),
                ('published_date', models.DateTimeField(auto_now_add=True)),
                ('last_edit_date', models.DateTimeField(auto_now=True)),
                ('content', tinymce.models.HTMLField(verbose_name='Content')),
                ('view_count', models.IntegerField(default=0)),
                ('draft', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ArticleView',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Duration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=80)),
            ],
        ),
        migrations.CreateModel(
            name='FreeView',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('article_view', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='articles.ArticleView')),
            ],
        ),
        migrations.CreateModel(
            name='Urgency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=80)),
            ],
        ),
    ]