from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from products.models import Product, Category
from stores.models import Store

BRANDS = {
    "Samsung": [
        ("Galaxy A35", "AMOLED display, balanced performance, long battery life"),
        ("Galaxy A55", "AMOLED display, excellent camera, strong battery life"),
        ("Galaxy S24", "flagship performance, bright AMOLED display, great camera"),
        (
            "Galaxy S24 Ultra",
            "premium display, powerful processor, advanced camera system",
        ),
        ("Galaxy A25", "large AMOLED display, good battery, affordable performance"),
        ("Galaxy M35", "large display, huge battery, gaming performance"),
        ("Galaxy M55", "AMOLED display, fast charging, powerful performance"),
        ("Galaxy S23 FE", "high performance, excellent camera, smooth AMOLED display"),
        ("Galaxy Z Flip 6", "foldable AMOLED display, premium camera, compact design"),
        ("Galaxy Z Fold 6", "large foldable display, powerful processor, multitasking"),
    ],
    "Apple": [
        ("iPhone 13", "OLED display, strong performance, excellent camera"),
        ("iPhone 14", "OLED display, reliable performance, excellent photography"),
        ("iPhone 15", "Super Retina display, strong camera, USB-C"),
        ("iPhone 15 Plus", "large OLED display, long battery life, excellent camera"),
        ("iPhone 15 Pro", "premium performance, titanium design, advanced camera"),
        (
            "iPhone 15 Pro Max",
            "large premium display, powerful chip, excellent zoom camera",
        ),
        ("iPhone 16", "OLED display, fast performance, improved camera"),
        ("iPhone 16 Plus", "large display, long battery life, strong performance"),
        ("iPhone 16 Pro", "premium display, powerful processor, advanced photography"),
        (
            "iPhone 16 Pro Max",
            "large premium display, excellent battery, pro camera system",
        ),
    ],
    "Xiaomi": [
        ("Redmi Note 13", "AMOLED display, good battery, excellent value"),
        ("Redmi Note 13 Pro", "high resolution camera, AMOLED display, fast charging"),
        (
            "Redmi Note 13 Pro+",
            "curved AMOLED display, fast charging, powerful performance",
        ),
        ("Redmi Note 14", "large AMOLED display, reliable battery, smooth performance"),
        ("Redmi Note 14 Pro", "high resolution camera, AMOLED display, strong battery"),
        ("Poco X6", "gaming performance, AMOLED display, fast charging"),
        ("Poco X6 Pro", "powerful gaming processor, high refresh rate display"),
        ("Poco F6", "flagship level performance, AMOLED display, fast charging"),
        ("Xiaomi 14", "compact flagship, excellent camera, bright AMOLED display"),
        (
            "Xiaomi 14 Ultra",
            "premium camera system, high-end performance, large display",
        ),
    ],
    "OnePlus": [
        ("OnePlus Nord CE 4", "smooth AMOLED display, strong battery, fast charging"),
        ("OnePlus Nord 4", "metal design, powerful performance, large AMOLED display"),
        (
            "OnePlus 11",
            "flagship performance, excellent camera, high refresh rate display",
        ),
        ("OnePlus 12", "powerful processor, premium display, excellent battery"),
        ("OnePlus 12R", "gaming performance, large AMOLED display, fast charging"),
        ("OnePlus Open", "foldable display, flagship performance, multitasking"),
        ("OnePlus Nord 3", "fast performance, AMOLED display, strong battery"),
        ("OnePlus Nord CE 3", "affordable AMOLED phone, good battery, fast charging"),
        ("OnePlus Ace 3", "high performance, gaming focused, fast charging"),
        ("OnePlus Ace 5", "powerful processor, high refresh rate display, gaming"),
    ],
    "Google": [
        ("Pixel 7", "excellent computational photography, OLED display"),
        ("Pixel 7 Pro", "advanced camera system, large OLED display"),
        ("Pixel 8", "excellent camera, clean Android experience, bright display"),
        ("Pixel 8 Pro", "premium camera, large display, powerful AI features"),
        ("Pixel 8a", "affordable camera phone, OLED display, strong battery"),
        ("Pixel 9", "advanced AI features, excellent camera, OLED display"),
        ("Pixel 9 Pro", "pro camera system, bright display, powerful AI features"),
        ("Pixel 9 Pro XL", "large display, premium camera, long battery life"),
        ("Pixel 7a", "compact camera phone, OLED display, good performance"),
        ("Pixel Fold", "foldable OLED display, multitasking, flagship performance"),
    ],
    "OPPO": [
        ("Reno 11", "portrait camera, AMOLED display, fast charging"),
        ("Reno 11 Pro", "premium portrait camera, curved AMOLED display"),
        ("Reno 12", "AI photography, AMOLED display, strong battery"),
        ("Reno 12 Pro", "advanced portrait camera, premium display"),
        ("Find X6", "flagship camera system, AMOLED display, powerful performance"),
        ("Find X6 Pro", "professional camera system, premium performance"),
        ("Find X7", "high-end camera, bright display, fast charging"),
        (
            "Find X7 Ultra",
            "advanced camera system, premium display, flagship processor",
        ),
        ("A79", "large display, good battery, affordable performance"),
        ("A98", "fast charging, AMOLED display, balanced performance"),
    ],
    "Vivo": [
        ("V29", "portrait photography, curved AMOLED display, fast charging"),
        ("V30", "excellent portrait camera, large AMOLED display"),
        ("V30 Pro", "ZEISS camera system, premium display, strong battery"),
        ("V40", "portrait camera, bright AMOLED display, long battery"),
        ("V40 Pro", "advanced camera, curved display, fast charging"),
        ("X90", "flagship performance, professional camera, AMOLED display"),
        ("X100", "powerful processor, advanced camera system, large display"),
        ("X100 Pro", "premium photography, flagship performance, fast charging"),
        ("Y100", "affordable AMOLED phone, good battery"),
        ("Y200", "large display, strong battery, smooth performance"),
    ],
    "Realme": [
        ("12 Pro", "portrait camera, curved AMOLED display, fast charging"),
        ("12 Pro+", "periscope camera, premium AMOLED display, strong battery"),
        ("GT Neo 5", "gaming performance, high refresh rate display, fast charging"),
        ("GT 6", "flagship performance, gaming display, large battery"),
        ("GT 6T", "powerful gaming processor, AMOLED display, fast charging"),
        ("C67", "large display, good battery, affordable smartphone"),
        ("C75", "large battery, durable design, affordable performance"),
        ("Narzo 70", "gaming performance, AMOLED display, fast charging"),
        ("Narzo 70 Pro", "Sony camera sensor, AMOLED display, strong battery"),
        ("11 Pro", "AMOLED display, fast charging, portrait photography"),
    ],
    "Honor": [
        ("X8b", "large AMOLED display, good camera, slim design"),
        ("X9b", "durable curved display, large battery, strong performance"),
        ("200", "portrait photography, AMOLED display, fast charging"),
        ("200 Pro", "advanced portrait camera, premium display"),
        ("90", "high resolution camera, curved AMOLED display"),
        ("90 Pro", "high-end camera, bright AMOLED display, fast charging"),
        ("Magic 5 Pro", "premium camera system, flagship performance"),
        ("Magic 6 Pro", "advanced AI camera, premium display, powerful processor"),
        ("Magic V2", "thin foldable phone, large OLED display, flagship performance"),
        ("X7c", "large battery, affordable performance, durable design"),
    ],
}


RAM_OPTIONS = [8, 8, 12, 12, 16]
STORAGE_OPTIONS = [128, 256, 256, 512]
BATTERY_OPTIONS = [4500, 5000, 5000, 5500]
REFRESH_RATES = [90, 120, 120, 144]


class Command(BaseCommand):
    help = "Create 100 realistic test smartphone products."

    @transaction.atomic
    def handle(self, *args, **options):
        store = Store.objects.first()

        if not store:
            self.stdout.write(self.style.ERROR("No Store found."))
            return

        category = Category.objects.filter(store=store, name__iexact="Phones").first()

        if not category:
            self.stdout.write(
                self.style.ERROR(
                    f'Category "Phones" was not found for store "{store}".'
                )
            )
            return

        created_count = 0
        updated_count = 0

        products = []

        index = 0

        for brand, phones in BRANDS.items():
            for model_name, features in phones:
                index += 1

                ram = RAM_OPTIONS[(index - 1) % len(RAM_OPTIONS)]
                storage = STORAGE_OPTIONS[(index - 1) % len(STORAGE_OPTIONS)]
                battery = BATTERY_OPTIONS[(index - 1) % len(BATTERY_OPTIONS)]
                refresh_rate = REFRESH_RATES[(index - 1) % len(REFRESH_RATES)]

                price = Decimal(str(5000 + ((index * 137) % 30000)))

                cost_price = price * Decimal("0.72")
                discount_price = price * Decimal("0.90")

                description = (
                    f"{features}. "
                    f"{ram}GB RAM, {storage}GB storage, "
                    f"{battery}mAh battery, "
                    f"{refresh_rate}Hz display. "
                    f"Suitable for everyday use, photography, "
                    f"gaming, and multimedia."
                )

                sku = f"PHONE-{index:03d}"

                product, created = Product.objects.update_or_create(
                    store=store,
                    sku=sku,
                    defaults={
                        "category": category,
                        "name": f"{brand} {model_name}",
                        "description": description,
                        "cost_price": cost_price.quantize(Decimal("0.01")),
                        "price": price,
                        "discount_price": discount_price.quantize(Decimal("0.01")),
                        "is_active": True,
                        "stock_quantity": 5 + (index % 46),
                    },
                )

                products.append(product)

                if created:
                    created_count += 1
                else:
                    updated_count += 1

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created: {created_count}, Updated: {updated_count}"
            )
        )
        self.stdout.write(self.style.SUCCESS(f"Total test products: {len(products)}"))
