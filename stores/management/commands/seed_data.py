import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction

from stores.models import *

User = get_user_model()


# =============================
# 🔧 HELPERS
# =============================
def fake_image(name):
    return ContentFile(b"filecontent", name=name)


def rand_price():
    return Decimal(random.randint(10, 2000))


def rand_discount():
    return random.choice([0, 5, 10, 15, 20])


# =============================
# 🌍 MULTI LANGUAGE DATA
# =============================
STORE_CATEGORIES = [
    ("Electronics", "إلكترونيات", "Électronique", "electronics"),
    ("Fashion", "موضة", "Mode", "fashion"),
    ("Furniture", "أثاث", "Meubles", "furniture"),
]

PRODUCT_CATEGORIES = {
    "electronics": [
        ("Smartphones", "هواتف", "Smartphones"),
        ("Laptops", "حواسيب", "Ordinateurs"),
    ],
    "fashion": [
        ("T-Shirts", "قمصان", "T-shirts"),
        ("Shoes", "أحذية", "Chaussures"),
    ]
}

COLORS = [
    ("Red", "أحمر", "Rouge", "#FF0000"),
    ("Blue", "أزرق", "Bleu", "#0000FF"),
    ("Black", "أسود", "Noir", "#000000"),
]

SIZES = [
    ("S", "صغير", "Petit"),
    ("M", "متوسط", "Moyen"),
    ("L", "كبير", "Grand"),
]

STORAGE = [
    ("64GB", "64 جيجا", "64 Go"),
    ("128GB", "128 جيجا", "128 Go"),
]



# =============================
# 🧠 COMMAND
# =============================
class Command(BaseCommand):
    help = "Full advanced seeding"
    
    @transaction.atomic
    def handle(self, *args, **kwargs):

        # =============================
        # 🧹 CLEAN DATABASE
        # =============================
        self.stdout.write("🧹 Cleaning database...")

        OrderStatusHistory.objects.all().delete()
        Payment.objects.all().delete()
        ShippingAddress.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()

        ProductImage.objects.all().delete()
        ProductVariant.objects.all().delete()
        Product.objects.all().delete()

        ProductAttribute.objects.all().delete()

        Store.objects.all().delete()
        ProductCategory.objects.all().delete()
        StoreCategory.objects.all().delete()

        self.stdout.write("✅ Database cleaned!")

        # =============================
        # 🚀 START SEEDING
        # =============================
        self.stdout.write("🚀 Start FULL seeding...")

        # =============================
        # 👤 USERS
        # =============================
        users = []
        for i in range(3):
            user, _ = User.objects.get_or_create(
                username=f"user{i}",
                defaults={"email": f"user{i}@test.com"}
            )
            user.set_password("123456")
            user.save()
            users.append(user)

        # =============================
        # 🏬 STORE CATEGORIES
        # =============================
        store_categories = []
        for en, ar, fr, slug in STORE_CATEGORIES:
            obj, _ = StoreCategory.objects.get_or_create(
                slug=slug,
                defaults=dict(
                    name_en=en,
                    name_ar=ar,
                    name_fr=fr,
                )
            )
            store_categories.append(obj)

        # =============================
        # 📦 PRODUCT CATEGORIES
        # =============================
        product_categories = []
        for sc in store_categories:
            for en, ar, fr in PRODUCT_CATEGORIES.get(sc.slug, []):
                pc, _ = ProductCategory.objects.get_or_create(
                    store_category=sc,
                    name_en=en,
                    defaults=dict(name_ar=ar, name_fr=fr)
                )
                product_categories.append(pc)

        # =============================
        # 🏪 STORES
        # =============================
        stores = []
        for i, user in enumerate(users):
            store, _ = Store.objects.get_or_create(
                owner=user,
                defaults=dict(
                    subdomain=f"store{i}",
                    name_en=f"Store {i}",
                    name_ar=f"متجر {i}",
                    name_fr=f"Magasin {i}",

                    description_en="Best products",
                    description_ar="أفضل المنتجات",
                    description_fr="Meilleurs produits",

                    tagline_en="Shop now",
                    tagline_ar="تسوق الآن",
                    tagline_fr="Achetez maintenant",

                    logo=fake_image(f"logo{i}.jpg"),
                    banner=fake_image(f"banner{i}.jpg"),

                    is_verified=True,
                    is_active=True,
                    is_featured=True,

                    watsapp_number="+213555000000",
                    facebook_url="https://facebook.com",
                    instagram_url="https://instagram.com",
                    website_url="https://example.com"
                )
            )
            store.categories.set(store_categories)
            stores.append(store)

        # =============================
        # 🎨 ATTRIBUTES
        # =============================
        attributes = []

        for en, ar, fr, hex_code in COLORS:
            attributes.append(ProductAttribute.objects.create(
                category="COLOR",
                value_en=en, value_ar=ar, value_fr=fr,
                color_code=hex_code
            ))

        for en, ar, fr in SIZES:
            attributes.append(ProductAttribute.objects.create(
                category="SIZE",
                value_en=en, value_ar=ar, value_fr=fr
            ))

        for en, ar, fr in STORAGE:
            attributes.append(ProductAttribute.objects.create(
                category="STORAGE",
                value_en=en, value_ar=ar, value_fr=fr
            ))

        # =============================
        # 🛍 PRODUCTS + VARIANTS
        # =============================
        products = []
        for store in stores:
            for i in range(5):
                category = random.choice(product_categories)

                product = Product.objects.create(
                    store=store,
                    category=category,

                    name_en=f"Product {i}",
                    name_ar=f"منتج {i}",
                    name_fr=f"Produit {i}",

                    base_price=rand_price(),
                    discount=rand_discount(),

                    main_image=fake_image(f"product{i}.jpg"),

                    is_active=True,
                    is_featured=random.choice([True, False]),
                    is_new_arrival=random.choice([True, False]),
                    is_on_sale=random.choice([True, False]),
                )

                # Images
                for img_i in range(2):
                    ProductImage.objects.create(
                        product=product,
                        image=fake_image(f"p{i}_{img_i}.jpg"),
                        alt_text_en="Product image",
                        alt_text_ar="صورة المنتج",
                        alt_text_fr="Image produit"
                    )

                # Variants
                for v in range(3):
                    variant = ProductVariant.objects.create(
                        product=product,
                        stock=random.randint(1, 100),
                        sku=f"SKU-{store.id}-{i}-{v}",
                        price_override=rand_price()
                    )

                    variant.attribute_values.set(
                        random.sample(attributes, k=2)
                    )

                products.append(product)

        # =============================
        # 🧾 ORDERS
        # =============================
        for i in range(5):
            customer = random.choice(users)
            store = random.choice(stores)

            order = Order.objects.create(
                customer=customer,
                store=store,
                status="PENDING",
                total_price=0,
                notes="Test order"
            )

            total = 0

            for _ in range(3):
                product = random.choice(products)
                variant = product.variants.first()

                price = product.discounted_price
                qty = random.randint(1, 3)

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    variant=variant,
                    quantity=qty,
                    price=price
                )

                total += price * qty

            order.total_price = total
            order.save()

            # Shipping
            ShippingAddress.objects.create(
                order=order,
                full_name="Test User",
                phone="0555000000",
                address="Street 123",
                city="Tlemcen",
                state="Tlemcen",
                postal_code="13000",
                country="Algeria"
            )

            # Payment
            Payment.objects.create(
                order=order,
                method=random.choice(["CASH", "CARD", "CCP"]),
                status="PAID",
                transaction_id=f"TXN-{i}"
            )

            # Status history
            for status in ["PENDING", "CONFIRMED", "PROCESSING", "DELIVERED"]:
                OrderStatusHistory.objects.create(
                    order=order,
                    status=status,
                    note=f"{status} step"
                )

        self.stdout.write(self.style.SUCCESS("✅ FULL DATA SEEDED SUCCESSFULLY"))