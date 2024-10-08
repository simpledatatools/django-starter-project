# Generated by Django 5.0.4 on 2024-09-22 14:48

import core.utils
import django.contrib.auth.models
import django.contrib.auth.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailLinkModel',
            fields=[
                ('id', models.CharField(default=core.utils.generate_model_id, editable=False, max_length=32, primary_key=True, serialize=False)),
                ('key', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_delete', models.BooleanField(blank=True, default=False, null=True)),
                ('new_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('link_type', models.CharField(blank=True, choices=[('register', 'Register'), ('reset_password', 'Reset Password'), ('password_change', 'Password Change'), ('email_change', 'Email Change')], default='', max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserExtras',
            fields=[
                ('id', models.CharField(default=core.utils.generate_model_id, editable=False, max_length=32, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_active', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'User Extras',
                'verbose_name_plural': 'User Extras',
            },
        ),
        migrations.CreateModel(
            name='UserPasscode',
            fields=[
                ('id', models.CharField(default=core.utils.generate_model_id, editable=False, max_length=32, primary_key=True, serialize=False)),
                ('passcode', models.CharField(editable=False, max_length=64)),
                ('name', models.CharField(max_length=255, null=True)),
                ('view_summary', models.BooleanField(default=True)),
                ('view_live', models.BooleanField(default=True)),
                ('view_history', models.BooleanField(default=True)),
                ('view_checkins', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='active', max_length=10)),
            ],
            options={
                'verbose_name': 'User Passcodes',
                'verbose_name_plural': 'User Passcodes',
            },
        ),
        migrations.CreateModel(
            name='VerifyCode',
            fields=[
                ('id', models.CharField(default=core.utils.generate_model_id, editable=False, max_length=32, primary_key=True, serialize=False)),
                ('code', models.CharField(blank=True, max_length=5, null=True)),
                ('key', models.CharField(blank=True, max_length=64, null=True)),
                ('email', models.CharField(blank=True, max_length=1000, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(blank=True, default='pending', max_length=32, null=True)),
                ('code_type', models.CharField(blank=True, choices=[('register', 'Register'), ('reset_password', 'Reset Password'), ('password_change', 'Password Change'), ('email_change', 'Email Change')], default='', max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('display_name', models.CharField(blank=True, max_length=250, null=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
