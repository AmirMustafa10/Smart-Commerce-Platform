from django.db import migrations
from pgvector.django import VectorExtension


class Migration(migrations.Migration):

    dependencies = [
        (
            "products",
            "0007_remove_product_is_out_of_stock",
        ),
    ]

    operations = [
        VectorExtension(),
    ]
