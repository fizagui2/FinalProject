from django.db import migrations

NEW_CATEGORY_NAMES = ['PlayStation', 'Xbox', 'PC', 'General', 'News', 'Tips']
RETIRED_CATEGORY_NAMES = ['Nintendo', 'Pokémon', 'Retro Gaming']


def update_categories(apps, schema_editor):
    Category = apps.get_model('final_app', 'Category')
    Post = apps.get_model('final_app', 'Post')

    general, _ = Category.objects.get_or_create(name='General')

    for name in RETIRED_CATEGORY_NAMES:
        try:
            retired = Category.objects.get(name=name)
        except Category.DoesNotExist:
            continue
        Post.objects.filter(category=retired).update(category=general)
        retired.delete()

    pc_gaming = Category.objects.filter(name='PC Gaming').first()
    if pc_gaming:
        pc_gaming.name = 'PC'
        pc_gaming.save()
    else:
        Category.objects.get_or_create(name='PC')

    for name in NEW_CATEGORY_NAMES:
        Category.objects.get_or_create(name=name)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('final_app', '0003_seed_categories'),
    ]

    operations = [
        migrations.RunPython(update_categories, noop),
    ]
