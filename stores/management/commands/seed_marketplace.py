from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from accounts.models import UserProfile

from stores.models import (
    StoreCategory,
    ProductCategory,
    Store
)


User = get_user_model()



class Command(BaseCommand):
    help = "Seed marketplace data"


    def handle(self,*args,**kwargs):

        
        categories = [

            {
                "en":"Fashion",
                "ar":"الموضة والأزياء",
                "fr":"Mode",
                "products":[

                    ("Women's Watches","ساعات نسائية","Montres femmes"),
                    ("Men's Watches","ساعات رجالية","Montres hommes"),
                    ("Clothes","ملابس","Vêtements"),
                    ("Shoes","أحذية","Chaussures"),
                    ("Bags","حقائب","Sacs"),
                    ("Jewelry","مجوهرات","Bijoux"),
                    ("Accessories","إكسسوارات","Accessoires"),
                    ("Sunglasses","نظارات شمسية","Lunettes"),
                    ("Belts","أحزمة","Ceintures"),
                    ("Hats","قبعات","Chapeaux"),
                    ("Sports Wear","ملابس رياضية","Vêtements sportifs"),
                    ("Kids Fashion","أزياء أطفال","Mode enfants"),

                ]
            },


            {
                "en":"Electronics",
                "ar":"الإلكترونيات",
                "fr":"Électronique",

                "products":[

                    ("Smartphones","هواتف ذكية","Smartphones"),
                    ("Laptops","حاسوب محمول","Ordinateurs portables"),
                    ("Computers","حواسيب","Ordinateurs"),
                    ("Tablets","أجهزة لوحية","Tablettes"),
                    ("Smart Watches","ساعات ذكية","Montres connectées"),
                    ("Headphones","سماعات","Casques"),
                    ("Cameras","كاميرات","Caméras"),
                    ("Televisions","تلفاز","Télévisions"),
                    ("Gaming","ألعاب","Jeux"),
                    ("Printers","طابعات","Imprimantes"),
                    ("Chargers","شواحن","Chargeurs"),
                    ("Power Banks","بطاريات متنقلة","Batteries"),

                ]
            },


            {
                "en":"Home & Kitchen",
                "ar":"المنزل والمطبخ",
                "fr":"Maison et cuisine",

                "products":[

                    ("Kitchen Tools","أدوات مطبخ","Outils cuisine"),
                    ("Cookware","أواني طبخ","Ustensiles"),
                    ("Furniture","أثاث","Meubles"),
                    ("Sofas","أرائك","Canapés"),
                    ("Beds","أسرة","Lits"),
                    ("Tables","طاولات","Tables"),
                    ("Lighting","إضاءة","Éclairage"),
                    ("Decoration","ديكور","Décoration"),
                    ("Carpets","سجاد","Tapis"),
                    ("Curtains","ستائر","Rideaux"),
                    ("Storage","تخزين","Rangement"),

                ]
            },


            {
                "en":"Beauty",
                "ar":"الجمال والعناية",
                "fr":"Beauté",

                "products":[

                    ("Perfumes","عطور","Parfums"),
                    ("Makeup","مكياج","Maquillage"),
                    ("Skin Care","العناية بالبشرة","Soins peau"),
                    ("Hair Care","العناية بالشعر","Soins cheveux"),
                    ("Body Care","العناية بالجسم","Soins corps"),
                    ("Beauty Tools","أدوات تجميل","Outils beauté"),

                ]
            },


            {
                "en":"Food",
                "ar":"الأغذية والمشروبات",
                "fr":"Alimentation",

                "products":[

                    ("Coffee","قهوة","Café"),
                    ("Tea","شاي","Thé"),
                    ("Spices","توابل","Épices"),
                    ("Sweets","حلويات","Sucreries"),
                    ("Drinks","مشروبات","Boissons"),
                    ("Organic Food","غذاء عضوي","Produits bio"),

                ]
            },


            {
                "en":"Sports",
                "ar":"الرياضة",
                "fr":"Sport",

                "products":[

                    ("Fitness","لياقة","Fitness"),
                    ("Football","كرة القدم","Football"),
                    ("Running","الجري","Course"),
                    ("Cycling","دراجات","Cyclisme"),
                    ("Camping","تخييم","Camping"),
                    ("Swimming","سباحة","Natation"),

                ]
            },


            {
                "en":"Cars",
                "ar":"السيارات",
                "fr":"Automobile",

                "products":[

                    ("Car Parts","قطع سيارات","Pièces auto"),
                    ("Car Accessories","إكسسوارات سيارات","Accessoires auto"),
                    ("Tires","إطارات","Pneus"),
                    ("Car Cleaning","تنظيف سيارات","Nettoyage"),

                ]
            },


            {
                "en":"Kids",
                "ar":"الأطفال",
                "fr":"Enfants",

                "products":[

                    ("Toys","ألعاب أطفال","Jouets"),
                    ("Baby Clothes","ملابس أطفال","Vêtements bébé"),
                    ("Baby Care","عناية الأطفال","Soins bébé"),
                    ("School Supplies","لوازم مدرسية","Fournitures"),

                ]
            },


            {
                "en":"Services",
                "ar":"الخدمات",
                "fr":"Services",

                "products":[

                    ("Photography","تصوير","Photographie"),
                    ("Marketing","تسويق","Marketing"),
                    ("Design","تصميم","Design"),
                    ("Programming","برمجة","Programmation"),

                ]
            },

        ]
        # ProductCategory.objects.all().delete()
        # StoreCategory.objects.all().delete()
        # Store.objects.all().delete()
        # User.objects.filter(is_superuser=False).delete()
        categories = []
        created_categories=[]



        # =====================
        # STORE CATEGORIES
        # =====================

        for item in categories:


            category,created = StoreCategory.objects.get_or_create(

                name_en=item["en"],

                defaults={

                    "name_ar":item["ar"],

                    "name_fr":item["fr"],

                    "slug":slugify(item["en"])

                }

            )


            created_categories.append(category)



            for product in item["products"]:


                ProductCategory.objects.get_or_create(

                    store_category=category,

                    name_en=product[0],

                    defaults={

                        "name_ar":product[1],

                        "name_fr":product[2]

                    }

                )


        # ============================
        # CREATE STORE OWNERS
        # ============================
        stores_data = [

            {
                "name_en": "Luna Fashion",
                "name_ar": "لونا للأزياء",
                "name_fr": "Luna Mode",
                "categories": [
                    "Fashion"
                ],
                "description_en": "Women's fashion, accessories and elegant styles",
                "description_ar": "ملابس نسائية وإكسسوارات وتصاميم أنيقة",
                "description_fr": "Mode femme, accessoires et styles élégants",
            },


            {
                "name_en": "Time House",
                "name_ar": "دار الساعات",
                "name_fr": "Maison des Montres",
                "categories": [
                    "Fashion"
                ],
                "description_en": "Luxury watches and accessories",
                "description_ar": "ساعات فاخرة وإكسسوارات",
                "description_fr": "Montres de luxe et accessoires",
            },


            {
                "name_en": "Tech Zone",
                "name_ar": "منطقة التقنية",
                "name_fr": "Zone Tech",
                "categories": [
                    "Electronics"
                ],
                "description_en": "Smartphones, computers and electronic devices",
                "description_ar": "هواتف وحواسيب وأجهزة إلكترونية",
                "description_fr": "Téléphones, ordinateurs et appareils électroniques",
            },


            {
                "name_en": "Mobile World",
                "name_ar": "عالم الهواتف",
                "name_fr": "Monde Mobile",
                "categories": [
                    "Electronics"
                ],
                "description_en": "Phones, accessories and smart devices",
                "description_ar": "هواتف وملحقات وأجهزة ذكية",
                "description_fr": "Téléphones et accessoires",
            },


            {
                "name_en": "Home Touch",
                "name_ar": "لمسة منزلية",
                "name_fr": "Touche Maison",
                "categories": [
                    "Home & Kitchen"
                ],
                "description_en": "Furniture and home decoration",
                "description_ar": "أثاث وديكور منزلي",
                "description_fr": "Meubles et décoration",
            },


            {
                "name_en": "Kitchen Pro",
                "name_ar": "مطبخ برو",
                "name_fr": "Cuisine Pro",
                "categories": [
                    "Home & Kitchen"
                ],
                "description_en": "Kitchen tools and cookware",
                "description_ar": "أدوات المطبخ وأواني الطبخ",
                "description_fr": "Ustensiles et cuisine",
            },


            {
                "name_en": "Beauty Line",
                "name_ar": "خط الجمال",
                "name_fr": "Beauty Line",
                "categories": [
                    "Beauty"
                ],
                "description_en": "Perfumes and beauty products",
                "description_ar": "عطور ومنتجات تجميل",
                "description_fr": "Parfums et beauté",
            },


            {
                "name_en": "Pure Care",
                "name_ar": "العناية الطبيعية",
                "name_fr": "Soin Naturel",
                "categories": [
                    "Beauty"
                ],
                "description_en": "Skin and body care products",
                "description_ar": "منتجات العناية بالبشرة والجسم",
                "description_fr": "Soins peau et corps",
            },


            {
                "name_en": "Fit Life",
                "name_ar": "حياة رياضية",
                "name_fr": "Vie Sportive",
                "categories": [
                    "Sports"
                ],
                "description_en": "Fitness and sports equipment",
                "description_ar": "معدات رياضية ولياقة",
                "description_fr": "Équipements sportifs",
            },


            {
                "name_en": "Auto Parts Plus",
                "name_ar": "قطع سيارات بلس",
                "name_fr": "Auto Pièces Plus",
                "categories": [
                    "Cars"
                ],
                "description_en": "Car parts and accessories",
                "description_ar": "قطع سيارات وإكسسوارات",
                "description_fr": "Pièces auto et accessoires",
            },


        ]

        stores_data = [

    {
        "name_en": "Pixel Studio",
        "name_ar": "استوديو بيكسل",
        "name_fr": "Studio Pixel",
        "categories": ["Services"],
        "description_en": "Professional photography, video production and visual content creation.",
        "description_ar": "تصوير احترافي وإنتاج فيديو وصناعة محتوى بصري.",
        "description_fr": "Photographie professionnelle, production vidéo et création de contenu visuel."
    },

    {
        "name_en": "Growth Hub",
        "name_ar": "مركز النمو",
        "name_fr": "Growth Hub",
        "categories": ["Services"],
        "description_en": "Digital marketing, advertising campaigns and brand growth solutions.",
        "description_ar": "التسويق الرقمي والحملات الإعلانية وحلول تطوير العلامات التجارية.",
        "description_fr": "Marketing digital, campagnes publicitaires et croissance des marques."
    },

    {
        "name_en": "Creative Spark",
        "name_ar": "الشرارة الإبداعية",
        "name_fr": "Étincelle Créative",
        "categories": ["Services"],
        "description_en": "Logo design, branding and creative visual identity solutions.",
        "description_ar": "تصميم الشعارات والهويات البصرية والحلول الإبداعية.",
        "description_fr": "Création de logos, identité visuelle et solutions créatives."
    },

    {
        "name_en": "Code Factory",
        "name_ar": "مصنع البرمجيات",
        "name_fr": "Usine Logicielle",
        "categories": ["Services"],
        "description_en": "Websites, mobile applications and custom software development.",
        "description_ar": "تطوير المواقع والتطبيقات والحلول البرمجية المخصصة.",
        "description_fr": "Développement web, applications mobiles et logiciels sur mesure."
    },

    {
        "name_en": "SEO Masters",
        "name_ar": "خبراء السيو",
        "name_fr": "Experts SEO",
        "categories": ["Services"],
        "description_en": "SEO optimization, website audits and search engine visibility improvement.",
        "description_ar": "تهيئة محركات البحث وتحليل المواقع وتحسين الظهور.",
        "description_fr": "Optimisation SEO, audits web et amélioration de la visibilité."
    },

    {
        "name_en": "Social Boost",
        "name_ar": "سوشيال بوست",
        "name_fr": "Social Boost",
        "categories": ["Services"],
        "description_en": "Social media management and content marketing services.",
        "description_ar": "إدارة صفحات التواصل الاجتماعي وصناعة المحتوى.",
        "description_fr": "Gestion des réseaux sociaux et marketing de contenu."
    },

    {
        "name_en": "App Vision",
        "name_ar": "رؤية التطبيقات",
        "name_fr": "Vision App",
        "categories": ["Services"],
        "description_en": "Mobile app design and development for Android and iOS.",
        "description_ar": "تصميم وتطوير تطبيقات أندرويد و iOS.",
        "description_fr": "Conception et développement d'applications Android et iOS."
    },

    {
        "name_en": "Brand Makers",
        "name_ar": "صناع العلامات",
        "name_fr": "Créateurs de Marques",
        "categories": ["Services"],
        "description_en": "Complete branding and corporate identity services.",
        "description_ar": "خدمات بناء العلامات التجارية والهويات المؤسسية.",
        "description_fr": "Services complets de branding et identité d'entreprise."
    }
    ]
        
        for index, data in enumerate(stores_data, start=14):


            email = f"{slugify(data['name_en'])}@market.com"


            user, created = User.objects.get_or_create(

                email=email,

                defaults={

                    "username":
                    slugify(data["name_en"]),


                    "first_name":
                    data["name_en"].split()[0],


                    "last_name":
                    "Owner",


                    "first_name_ar":
                    data["name_ar"].split()[0],


                    "last_name_ar":
                    "صاحب المتجر",


                    "phone":
                    f"055000{index:04d}",


                    "role":
                    User.Role.STORE_OWNER,


                    "is_active":
                    True,

                }

            )


            if created:

                user.set_password(
                    "12345678"
                )

                user.save()



            # ======================
            # PROFILE
            # ======================


            UserProfile.objects.get_or_create(

                user=user,

                defaults={


                    "bio_en":
                    data["description_en"],


                    "bio_ar":
                    data["description_ar"],


                    "bio_fr":
                    data["description_fr"],



                    "company_name":
                    data["name_en"],



                    "address":
                    "Algeria",



                    "is_verified":
                    True,

                }

            )



            # ======================
            # STORE
            # ======================


            store, created = Store.objects.get_or_create(

                owner=user,

                defaults={


                    "subdomain":
                    f"{slugify(data['name_en'])}-{index}",



                    "name_en":
                    data["name_en"],


                    "name_ar":
                    data["name_ar"],


                    "name_fr":
                    data["name_fr"],



                    "description_en":
                    data["description_en"],


                    "description_ar":
                    data["description_ar"],


                    "description_fr":
                    data["description_fr"],



                    "tagline_en":
                    "Quality products and trusted service",


                    "tagline_ar":
                    "منتجات عالية الجودة وخدمة موثوقة",


                    "tagline_fr":
                    "Produits de qualité et service fiable",



                    "watsapp_number":
                    user.phone,



                    "facebook_url":
                    "https://facebook.com",


                    "instagram_url":
                    "https://instagram.com",


                    "twitter_url":
                    "https://twitter.com",


                    "linkedin_url":
                    "https://linkedin.com",


                    "website_url":
                    "https://example.com",



                    "is_verified":
                    True,


                    "is_featured":
                    True,


                    "is_active":
                    True,


                }

            )



            # attach categories

            for cat in data["categories"]:


                category = StoreCategory.objects.get(

                    name_en=cat

                )


                store.categories.add(category)


# python manage.py seed_marketplace