from django.db import migrations

CATEGORY_NAMES = [
    'PlayStation',
    'Xbox',
    'Nintendo',
    'Pokémon',
    'PC Gaming',
    'Retro Gaming',
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model('final_app', 'Category')
    for name in CATEGORY_NAMES:
        Category.objects.get_or_create(name=name)


def remove_seeded_categories(apps, schema_editor):
    Category = apps.get_model('final_app', 'Category')
    Category.objects.filter(name__in=CATEGORY_NAMES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('final_app', '0002_post_comment_vote'),
    ]

    operations = [
        migrations.RunPython(seed_categories, remove_seeded_categories),
    ]
