from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import filemanager.models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                             related_name='subfolders', to='filemanager.folder')),
            ],
            options={'ordering': ['name'], 'unique_together': {('name', 'parent')}},
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to=filemanager.models.upload_to)),
                ('file_type', models.CharField(choices=[('image', 'Image'), ('document', 'Document'),
                                                         ('video', 'Video'), ('audio', 'Audio'),
                                                         ('archive', 'Archive'), ('other', 'Other')],
                                               default='other', max_length=20)),
                ('size', models.PositiveBigIntegerField(default=0)),
                ('uploaded_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('folder', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                             related_name='files', to='filemanager.folder')),
            ],
            options={'ordering': ['name']},
        ),
    ]
