from __future__ import annotations

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("orgs", "0002_organization_base_color_organization_logo"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="organization",
            name="base_color",
        ),
        migrations.RemoveField(
            model_name="organization",
            name="logo",
        ),
        migrations.AddField(
            model_name="organization",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="membership",
            name="role",
            field=models.CharField(choices=[("admin", "Admin"), ("member", "Member")], default="member", max_length=16),
        ),
    ]
