from django.db import migrations


def seed_products(apps, schema_editor):
    Category = apps.get_model("products", "Category")
    Product = apps.get_model("products", "Product")

    categories = {
        "hops": "Hops",
        "malts": "Malts",
        "yeast": "Yeast",
        "adjuncts": "Adjuncts",
        "kits": "Kits",
    }

    cat_objs = {}
    for slug, name in categories.items():
        cat, _ = Category.objects.get_or_create(slug=slug, defaults={"name": name})
        cat_objs[slug] = cat

    products = [
        ("citra-hops", "Citra Hops", "Ideal for IPAs and Pale Ales", "5.99", "hops"),
        (
            "maris-otter-pale-malt",
            "Maris Otter Pale Malt",
            "Perfect for traditional ales",
            "2.50",
            "malts",
        ),
        (
            "safale-us-05-dry-ale-yeast",
            "SafAle US-05 Dry Ale Yeast",
            "Clean fermenting American ale yeast",
            "3.25",
            "yeast",
        ),
        ("cascade-hops", "Cascade Hops", "Great for dry hopping", "7.49", "hops"),
        (
            "caramel-malt-60l",
            "Caramel Malt 60L",
            "Improves body and head retention in darker beers",
            "3.00",
            "malts",
        ),
        ("saaz-hops", "Saaz Hops", "Essential noble hop for lagers", "4.75", "hops"),
        (
            "pilsner-malt",
            "Pilsner Malt",
            "Foundation for lagers and pilsners",
            "2.20",
            "malts",
        ),
        (
            "imperial-organic-yeast-a07",
            "Imperial Organic Yeast A07",
            "Great for American ales with citrus notes",
            "8.99",
            "yeast",
        ),
        (
            "centennial-hops",
            "Centennial Hops",
            "Often called Super Cascade",
            "6.20",
            "hops",
        ),
        (
            "mosaic-hops",
            "Mosaic Hops",
            "Complex tropical and berry profile for IPA",
            "9.50",
            "hops",
        ),
        (
            "west-coast-ipa-all-grain-kit",
            "West Coast IPA - All-Grain Kit",
            "Complete kit for classic West Coast IPA",
            "60.00",
            "kits",
        ),
        (
            "unmalted-wheat",
            "Unmalted Wheat",
            "Great for Belgian Witbier style",
            "1.80",
            "adjuncts",
        ),
    ]

    for slug, name, description, price, category_slug in products:
        Product.objects.get_or_create(
            slug=slug,
            defaults={
                "name": name,
                "description": description,
                "price": price,
                "category": cat_objs[category_slug],
                "is_active": True,
                "stock": 100,
                "popularity": 0,
            },
        )


def unseed_products(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    slugs = [
        "citra-hops",
        "maris-otter-pale-malt",
        "safale-us-05-dry-ale-yeast",
        "cascade-hops",
        "caramel-malt-60l",
        "saaz-hops",
        "pilsner-malt",
        "imperial-organic-yeast-a07",
        "centennial-hops",
        "mosaic-hops",
        "west-coast-ipa-all-grain-kit",
        "unmalted-wheat",
    ]
    Product.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_products, unseed_products),
    ]