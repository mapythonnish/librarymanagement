# Generated by Django 5.1.4 on 2024-12-05 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0002_rename_available_copies_book_copies_alter_book_isbn_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='available_copies',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
