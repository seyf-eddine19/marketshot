from django.core.management.base import BaseCommand
from django.utils.text import slugify
from decimal import Decimal
import itertools

from stores.models import (
    Store,
    StoreCategory,
    ProductCategory,
)

from stores.models import (
    Product,
    ProductAttribute,
    ProductVariant,
)

FASHION_PRODUCTS = {

"Women's Watches": [

    {
        "name_en": "Rose Gold Luxury Watch",
        "name_ar": "ساعة روز غولد فاخرة",
        "name_fr": "Montre Luxe Rose Gold",

        "description_en": "Elegant luxury watch with stainless steel strap and water resistance.",
        "description_ar": "ساعة فاخرة أنيقة بسوار من الفولاذ المقاوم للماء.",
        "description_fr": "Montre élégante avec bracelet en acier inoxydable.",

        "price": 8500,

        "attributes": {

            "COLOR": [
                ("Rose Gold","روز غولد","Or Rose","#B76E79",0),
                ("Gold","ذهبي","Doré","#FFD700",1200),
                ("Silver","فضي","Argent","#C0C0C0",600),
            ],

            "MATERIAL": [
                ("Stainless Steel","فولاذ مقاوم للصدأ","Acier inoxydable",0),
                ("Titanium","تيتانيوم","Titane",2500),
            ]
        }
    },

    {
        "name_en": "Classic Leather Watch",
        "name_ar": "ساعة جلد كلاسيكية",
        "name_fr": "Montre Cuir Classique",

        "price": 6200,

        "attributes": {

            "COLOR": [
                ("Black","أسود","Noir","#000000",0),
                ("Brown","بني","Marron","#8B4513",0),
                ("Blue","أزرق","Bleu","#0066CC",300),
            ],

            "MATERIAL": [
                ("Leather","جلد","Cuir",0),
                ("Premium Leather","جلد فاخر","Cuir Premium",1200),
            ]
        }
    },

    {
        "name_en": "Elegant Diamond Watch",
        "name_ar": "ساعة مرصعة أنيقة",
        "name_fr": "Montre Élégante",

        "price": 14500,

        "attributes": {

            "COLOR": [
                ("Silver","فضي","Argent","#C0C0C0",0),
                ("Gold","ذهبي","Doré","#FFD700",1800),
            ],

            "MATERIAL": [
                ("Steel","فولاذ","Acier",0),
            ]
        }
    }
],

"Men's Watches": [

    {
        "name_en": "Business Steel Watch",
        "name_ar": "ساعة أعمال فولاذية",
        "name_fr": "Montre Business",

        "price": 7800,

        "attributes": {

            "COLOR": [
                ("Silver","فضي","Argent","#C0C0C0",0),
                ("Black","أسود","Noir","#000000",500),
            ],

            "MATERIAL": [
                ("Steel","فولاذ","Acier",0),
            ]
        }
    },

    {
        "name_en": "Sport Chronograph Watch",
        "name_ar": "ساعة رياضية كرونوغراف",
        "name_fr": "Montre Sport",

        "price": 9900,

        "attributes": {

            "COLOR": [
                ("Black","أسود","Noir","#000000",0),
                ("Blue","أزرق","Bleu","#0066CC",600),
            ],

            "MATERIAL": [
                ("Rubber","مطاط","Caoutchouc",0),
                ("Steel","فولاذ","Acier",800),
            ]
        }
    },

    {
        "name_en": "Luxury Gold Watch",
        "name_ar": "ساعة ذهبية فاخرة",
        "name_fr": "Montre Luxe Or",

        "price": 18500,

        "attributes": {

            "COLOR": [
                ("Gold","ذهبي","Doré","#FFD700",0),
                ("Rose Gold","روز غولد","Or Rose","#B76E79",1200),
            ]
        }
    }
],

"Clothes": [

    {
        "name_en": "Premium T-Shirt",
        "name_ar": "قميص فاخر",
        "name_fr": "T-Shirt Premium",

        "price": 2200,

        "attributes": {

            "COLOR": [
                ("Black","أسود","Noir","#000000",0),
                ("White","أبيض","Blanc","#FFFFFF",0),
                ("Blue","أزرق","Bleu","#0066CC",200),
            ],

            "SIZE": [
                ("S","صغير","S",0),
                ("M","متوسط","M",0),
                ("L","كبير","L",100),
                ("XL","كبير جداً","XL",200),
            ],

            "MATERIAL": [
                ("Cotton","قطن","Coton",0),
                ("Organic Cotton","قطن عضوي","Coton Bio",500),
            ]
        }
    },

    {
        "name_en": "Urban Hoodie",
        "name_ar": "هودي عصري",
        "name_fr": "Hoodie Urbain",

        "price": 4500,

        "attributes": {

            "COLOR": [
                ("Black","أسود","Noir","#000000",0),
                ("Gray","رمادي","Gris","#808080",0),
            ],

            "SIZE": [
                ("M","متوسط","M",0),
                ("L","كبير","L",100),
                ("XL","كبير جداً","XL",200),
            ]
        }
    },

    {
        "name_en": "Summer Shirt",
        "name_ar": "قميص صيفي",
        "name_fr": "Chemise Été",

        "price": 3200,

        "attributes": {

            "COLOR": [
                ("White","أبيض","Blanc","#FFFFFF",0),
                ("Blue","أزرق","Bleu","#0066CC",100),
            ],

            "SIZE": [
                ("S","صغير","S",0),
                ("M","متوسط","M",0),
                ("L","كبير","L",100),
            ]
        }
    }
],

"Shoes": [

    {
        "name_en": "Running Sneakers",
        "name_ar": "حذاء جري",
        "name_fr": "Chaussures Running",

        "price": 6500,

        "attributes": {

            "COLOR": [
                ("Black","أسود","Noir","#000000",0),
                ("White","أبيض","Blanc","#FFFFFF",0),
                ("Red","أحمر","Rouge","#FF0000",300),
            ],

            "SIZE": [
                ("40","40","40",0),
                ("41","41","41",0),
                ("42","42","42",0),
                ("43","43","43",0),
                ("44","44","44",0),
            ]
        }
    },

    {
        "name_en": "Leather Formal Shoes",
        "name_ar": "حذاء جلد رسمي",
        "name_fr": "Chaussures Cuir",

        "price": 9500,

        "attributes": {

            "COLOR": [
                ("Black","أسود","Noir","#000000",0),
                ("Brown","بني","Marron","#8B4513",300),
            ],

            "SIZE": [
                ("40","40","40",0),
                ("41","41","41",0),
                ("42","42","42",0),
                ("43","43","43",0),
            ]
        }
    },

    {
        "name_en": "Casual Sneakers",
        "name_ar": "حذاء كاجوال",
        "name_fr": "Chaussures Décontractées",

        "price": 4800,

        "attributes": {

            "COLOR": [
                ("White","أبيض","Blanc","#FFFFFF",0),
                ("Blue","أزرق","Bleu","#0066CC",200),
                ("Gray","رمادي","Gris","#808080",200),
            ],

            "SIZE": [
                ("39","39","39",0),
                ("40","40","40",0),
                ("41","41","41",0),
                ("42","42","42",0),
                ("43","43","43",0),
            ]
        }
    }
]

}

ELECTRONICS_PRODUCTS = {
"Smartphones": [

    {
        "name_en": "Nova X Pro",
        "name_ar": "نوفا إكس برو",
        "name_fr": "Nova X Pro",
        "price": 68000,

        "attributes": {

            "COLOR": [
                ("Black","أسود","Noir","#000000",0),
                ("Blue","أزرق","Bleu","#0066CC",1000),
                ("Silver","فضي","Argent","#C0C0C0",1500),
            ],

            "STORAGE": [
                ("128 GB","128 جيجا","128 Go",0),
                ("256 GB","256 جيجا","256 Go",8000),
                ("512 GB","512 جيجا","512 Go",15000),
            ]
        }
    },

    {
        "name_en": "Galaxy Max",
        "name_ar": "جالاكسي ماكس",
        "name_fr": "Galaxy Max",
        "price": 89000,

        "attributes": {

            "COLOR": [
                ("Black","أسود","Noir","#000000",0),
                ("Green","أخضر","Vert","#008000",2000),
            ],

            "STORAGE": [
                ("256 GB","256 جيجا","256 Go",0),
                ("512 GB","512 جيجا","512 Go",12000),
            ]
        }
    },

    {
        "name_en": "Smart Lite",
        "name_ar": "سمارت لايت",
        "name_fr": "Smart Lite",
        "price": 43000,

        "attributes": {

            "COLOR": [
                ("White","أبيض","Blanc","#FFFFFF",0),
                ("Black","أسود","Noir","#000000",0),
            ],

            "STORAGE": [
                ("64 GB","64 جيجا","64 Go",0),
                ("128 GB","128 جيجا","128 Go",5000),
            ]
        }
    }
],

"Laptops": [

    {
        "name_en": "WorkBook Pro",
        "name_ar": "ورك بوك برو",
        "name_fr": "WorkBook Pro",
        "price": 95000,

        "attributes": {

            "COLOR": [
                ("Silver","فضي","Argent","#C0C0C0",0),
                ("Black","أسود","Noir","#000000",2000),
            ],

            "STORAGE": [
                ("256 SSD","256 SSD","256 SSD",0),
                ("512 SSD","512 SSD","512 SSD",9000),
                ("1TB SSD","1TB SSD","1TB SSD",18000),
            ]
        }
    },

    {
        "name_en": "Gamer X",
        "name_ar": "جيامر إكس",
        "name_fr": "Gamer X",
        "price": 165000,

        "attributes": {

            "COLOR": [
                ("Black","أسود","Noir","#000000",0),
            ],

            "STORAGE": [
                ("512 SSD","512 SSD","512 SSD",0),
                ("1TB SSD","1TB SSD","1TB SSD",12000),
            ]
        }
    },

    {
        "name_en": "Student Book",
        "name_ar": "ستودنت بوك",
        "name_fr": "Student Book",
        "price": 72000,

        "attributes": {

            "COLOR": [
                ("Gray","رمادي","Gris","#808080",0),
                ("Blue","أزرق","Bleu","#0066CC",1500),
            ],

            "STORAGE": [
                ("256 SSD","256 SSD","256 SSD",0),
                ("512 SSD","512 SSD","512 SSD",7000),
            ]
        }
    }
],

"Computers": [

    {
        "name_en": "Office PC",
        "name_ar": "حاسوب مكتبي للمكاتب",
        "name_fr": "PC Bureau",
        "price": 85000,

        "attributes": {

            "STORAGE": [
                ("512 SSD","512 SSD","512 SSD",0),
                ("1TB SSD","1TB SSD","1TB SSD",12000),
            ]
        }
    },

    {
        "name_en": "Gaming Beast",
        "name_ar": "وحش الألعاب",
        "name_fr": "Gaming Beast",
        "price": 210000,

        "attributes": {

            "STORAGE": [
                ("1TB SSD","1TB SSD","1TB SSD",0),
                ("2TB SSD","2TB SSD","2TB SSD",25000),
            ]
        }
    },

    {
        "name_en": "Home Desktop",
        "name_ar": "حاسوب منزلي",
        "name_fr": "PC Maison",
        "price": 69000,

        "attributes": {

            "STORAGE": [
                ("256 SSD","256 SSD","256 SSD",0),
                ("512 SSD","512 SSD","512 SSD",9000),
            ]
        }
    }
],

"Tablets": [

    {
        "name_en": "Tab Pro 11",
        "name_ar": "تاب برو 11",
        "name_fr": "Tab Pro 11",
        "price": 52000,

        "attributes": {

            "COLOR": [
                ("Silver","فضي","Argent","#C0C0C0",0),
                ("Black","أسود","Noir","#000000",1000),
            ],

            "STORAGE": [
                ("128 GB","128 جيجا","128 Go",0),
                ("256 GB","256 جيجا","256 Go",7000),
            ]
        }
    },

    {
        "name_en": "Media Tab",
        "name_ar": "ميديا تاب",
        "name_fr": "Media Tab",
        "price": 39000,

        "attributes": {

            "COLOR": [
                ("Gray","رمادي","Gris","#808080",0),
                ("Blue","أزرق","Bleu","#0066CC",1000),
            ],

            "STORAGE": [
                ("64 GB","64 جيجا","64 Go",0),
                ("128 GB","128 جيجا","128 Go",4500),
            ]
        }
    },

    {
        "name_en": "Kids Tablet",
        "name_ar": "تابلت للأطفال",
        "name_fr": "Tablette Enfants",
        "price": 28000,

        "attributes": {

            "COLOR": [
                ("Blue","أزرق","Bleu","#0066CC",0),
                ("Pink","وردي","Rose","#FFC0CB",0),
            ],

            "STORAGE": [
                ("32 GB","32 جيجا","32 Go",0),
                ("64 GB","64 جيجا","64 Go",3000),
            ]
        }
    }
],

"Smart Watches": [
    {
        "name_en": "Ultra Watch X",
        "name_ar": "ساعة ألترا X",
        "name_fr": "Montre Ultra X",
        "price": 22000,

        "attributes": {

            "COLOR": [
                ("Black","أسود","Noir","#000000",0),
                ("Silver","فضي","Argent","#C0C0C0",1500),
                ("Gold","ذهبي","Doré","#FFD700",2500),
            ],

            "MATERIAL": [
                ("Aluminum","ألمنيوم","Aluminium",0),
                ("Steel","فولاذ","Acier",2000),
            ]
        }
    },

    {
        "name_en": "Fit Smart Pro",
        "name_ar": "فيت سمارت برو",
        "name_fr": "Fit Smart Pro",
        "price": 18500,

        "attributes": {

            "COLOR": [
                ("Black","أسود","Noir","#000000",0),
                ("Blue","أزرق","Bleu","#0066CC",1000),
            ]
        }
    },

    {
        "name_en": "Health Watch",
        "name_ar": "ساعة صحية",
        "name_fr": "Montre Santé",
        "price": 16000,

        "attributes": {

            "COLOR": [
                ("Black","أسود","Noir","#000000",0),
                ("Green","أخضر","Vert","#008000",800),
            ]
        }
    }
],

"Headphones": [

    {
        "name_en": "Bass Boost Headphones",
        "name_ar": "سماعات باس",
        "name_fr": "Casque Bass Boost",
        "price": 6500,

        "attributes": {

            "COLOR": [
                ("Black","أسود","Noir","#000000",0),
                ("Red","أحمر","Rouge","#FF0000",500),
            ],

            "TYPE": [
                ("Wired","سلكي","Filaire",0),
                ("Wireless","لاسلكي","Sans fil",2000),
            ]
        }
    },

    {
        "name_en": "Noise Cancelling Pro",
        "name_ar": "سماعات عزل الضوضاء",
        "name_fr": "Casque Anti Bruit",
        "price": 14500,

        "attributes": {

            "COLOR": [
                ("Black","أسود","Noir","#000000",0),
                ("Silver","فضي","Argent","#C0C0C0",1000),
            ]
        }
    },

    {
        "name_en": "Gaming Headset X",
        "name_ar": "سماعة ألعاب",
        "name_fr": "Casque Gaming",
        "price": 9800,

        "attributes": {

            "COLOR": [
                ("Black","أسود","Noir","#000000",0),
                ("Blue","أزرق","Bleu","#0066CC",800),
            ]
        }
    }
],

"Cameras": [

    {
        "name_en": "Pro DSLR Camera",
        "name_ar": "كاميرا احترافية DSLR",
        "name_fr": "Caméra DSLR Pro",
        "price": 120000,

        "attributes": {

            "LENS": [
                ("18-55mm","18-55mm","18-55mm",0),
                ("18-135mm","18-135mm","18-135mm",15000),
            ]
        }
    },

    {
        "name_en": "Vlog Camera 4K",
        "name_ar": "كاميرا فلوغ 4K",
        "name_fr": "Caméra Vlog 4K",
        "price": 78000,

        "attributes": {

            "COLOR": [
                ("Black","أسود","Noir","#000000",0),
                ("White","أبيض","Blanc","#FFFFFF",2000),
            ]
        }
    },

    {
        "name_en": "Action Cam X",
        "name_ar": "كاميرا أكشن",
        "name_fr": "Action Cam",
        "price": 45000,

        "attributes": {

            "COLOR": [
                ("Black","أسود","Noir","#000000",0),
            ]
        }
    }
],

"Televisions": [

    {
        "name_en": "Smart TV 55 Inch",
        "name_ar": "تلفاز ذكي 55 بوصة",
        "name_fr": "TV Smart 55",
        "price": 98000,

        "attributes": {

            "SIZE": [
                ("43 Inch","43 بوصة","43 Pouces",0),
                ("55 Inch","55 بوصة","55 Pouces",12000),
                ("65 Inch","65 بوصة","65 Pouces",25000),
            ]
        }
    },

    {
        "name_en": "4K Ultra HD TV",
        "name_ar": "تلفاز 4K",
        "name_fr": "TV 4K",
        "price": 125000,

        "attributes": {

            "SIZE": [
                ("50 Inch","50 بوصة","50 Pouces",0),
                ("55 Inch","55 بوصة","55 Pouces",10000),
            ]
        }
    },

    {
        "name_en": "Budget TV",
        "name_ar": "تلفاز اقتصادي",
        "name_fr": "TV Économique",
        "price": 55000,

        "attributes": {

            "SIZE": [
                ("32 Inch","32 بوصة","32 Pouces",0),
                ("43 Inch","43 بوصة","43 Pouces",8000),
            ]
        }
    }
],

"Gaming": [

    {
        "name_en": "Play Console X",
        "name_ar": "كونسول ألعاب X",
        "name_fr": "Console X",
        "price": 95000,

        "attributes": {

            "STORAGE": [
                ("512 GB","512 جيجا","512 Go",0),
                ("1 TB","1 تيرا","1 To",15000),
            ]
        }
    },

    {
        "name_en": "Gaming Bundle Pro",
        "name_ar": "حزمة ألعاب",
        "name_fr": "Pack Gaming",
        "price": 120000,

        "attributes": {

            "OTHER": [
                ("Controller + Game","يد + لعبة","Manette + Jeu",0),
            ]
        }
    },

    {
        "name_en": "Arcade Mini",
        "name_ar": "أركيد صغير",
        "name_fr": "Mini Arcade",
        "price": 45000,

        "attributes": {

            "COLOR": [
                ("Black","أسود","Noir","#000000",0),
                ("Red","أحمر","Rouge","#FF0000",2000),
            ]
        }
    }
],

"Printers": [

    {
        "name_en": "Eco Tank Printer Pro",
        "name_ar": "طابعة إيكو تانك برو",
        "name_fr": "Imprimante Eco Tank",
        "price": 45000,

        "attributes": {

            "TYPE": [
                ("Inkjet","حبر","Jet d'encre",0),
                ("Laser","ليزر","Laser",12000),
            ]
        }
    },

    {
        "name_en": "Office Laser Printer",
        "name_ar": "طابعة مكتبية ليزر",
        "name_fr": "Imprimante Laser Bureau",
        "price": 62000,

        "attributes": {

            "COLOR": [
                ("Black","أسود","Noir","#000000",0),
            ],

            "TYPE": [
                ("Monochrome","أبيض وأسود","Noir et blanc",0),
                ("Color","ملونة","Couleur",8000),
            ]
        }
    },

    {
        "name_en": "Mini Portable Printer",
        "name_ar": "طابعة محمولة صغيرة",
        "name_fr": "Mini Imprimante Portable",
        "price": 18000,

        "attributes": {

            "COLOR": [
                ("White","أبيض","Blanc","#FFFFFF",0),
                ("Black","أسود","Noir","#000000",0),
            ]
        }
    }
],

"Chargers": [

    {
        "name_en": "Fast Charger 33W",
        "name_ar": "شاحن سريع 33 واط",
        "name_fr": "Chargeur Rapide 33W",
        "price": 2500,

        "attributes": {

            "TYPE": [
                ("USB-C","USB-C","USB-C",0),
                ("USB-A","USB-A","USB-A",0),
            ]
        }
    },

    {
        "name_en": "Super Fast Charger 65W",
        "name_ar": "شاحن فائق 65 واط",
        "name_fr": "Chargeur 65W",
        "price": 4500,

        "attributes": {

            "TYPE": [
                ("USB-C","USB-C","USB-C",0),
            ],

            "CABLE": [
                ("Included","مع كابل","Avec câble",0),
                ("No Cable","بدون كابل","Sans câble",-500),
            ]
        }
    },

    {
        "name_en": "Wireless Charger Pad",
        "name_ar": "شاحن لاسلكي",
        "name_fr": "Chargeur Sans Fil",
        "price": 3800,

        "attributes": {

            "COLOR": [
                ("Black","أسود","Noir","#000000",0),
                ("White","أبيض","Blanc","#FFFFFF",300),
            ]
        }
    }
],

"Power Banks": [

    {
        "name_en": "Power Bank 10000mAh",
        "name_ar": "بطارية متنقلة 10000",
        "name_fr": "Batterie 10000mAh",
        "price": 3500,

        "attributes": {

            "COLOR": [
                ("Black","أسود","Noir","#000000",0),
                ("Blue","أزرق","Bleu","#0066CC",200),
            ],

            "CAPACITY": [
                ("10000mAh","10000mAh","10000mAh",0),
                ("20000mAh","20000mAh","20000mAh",2500),
            ]
        }
    },

    {
        "name_en": "Fast Charge Power Bank",
        "name_ar": "بطارية شحن سريع",
        "name_fr": "Batterie Rapide",
        "price": 5200,

        "attributes": {

            "CAPACITY": [
                ("10000mAh","10000mAh","10000mAh",0),
                ("20000mAh","20000mAh","20000mAh",3000),
            ],

            "TYPE": [
                ("Fast Charge","شحن سريع","Charge rapide",0),
            ]
        }
    },

    {
        "name_en": "Slim Power Bank",
        "name_ar": "بطارية رفيعة",
        "name_fr": "Batterie Slim",
        "price": 2800,

        "attributes": {

            "COLOR": [
                ("Black","أسود","Noir","#000000",0),
                ("White","أبيض","Blanc","#FFFFFF",0),
            ]
        }
    }
]
}

HOME_KITCHEN_PRODUCTS = {

"Furniture": [

    {
        "name_en": "Modern Sofa 3-Seater",
        "name_ar": "أريكة عصرية 3 مقاعد",
        "name_fr": "Canapé Moderne 3 Places",
        "price": 85000,

        "attributes": {
            "COLOR": [
                ("Gray","رمادي","Gris","#808080",0),
                ("Beige","بيج","Beige","#F5F5DC",3000),
            ]
        }
    },

    {
        "name_en": "Wooden Coffee Table",
        "name_ar": "طاولة خشبية",
        "name_fr": "Table en Bois",
        "price": 22000,

        "attributes": {
            "MATERIAL": [
                ("Wood","خشب","Bois",0),
                ("MDF","MDF","MDF",-2000),
            ]
        }
    },

    {
        "name_en": "King Size Bed",
        "name_ar": "سرير كبير",
        "name_fr": "Lit King Size",
        "price": 120000,

        "attributes": {
            "SIZE": [
                ("Queen","كوين","Queen",0),
                ("King","كينغ","King",15000),
            ]
        }
    }
],

"Kitchen Tools": [

    {
        "name_en": "Non-Stick Cookware Set",
        "name_ar": "أواني طبخ غير لاصقة",
        "name_fr": "Set Ustensiles Antiadhésifs",
        "price": 15000,

        "attributes": {
            "PIECES": [
                ("5 Pieces","5 قطع","5 pièces",0),
                ("10 Pieces","10 قطع","10 pièces",6000),
            ]
        }
    },

    {
        "name_en": "Electric Blender",
        "name_ar": "خلاط كهربائي",
        "name_fr": "Mixeur Électrique",
        "price": 7800,

        "attributes": {
            "POWER": [
                ("500W","500 واط","500W",0),
                ("1000W","1000 واط","1000W",3000),
            ]
        }
    },

    {
        "name_en": "Air Fryer",
        "name_ar": "قلاية هوائية",
        "name_fr": "Friteuse Sans Huile",
        "price": 18000,

        "attributes": {
            "CAPACITY": [
                ("3L","3 لتر","3L",0),
                ("5L","5 لتر","5L",5000),
            ]
        }
    }
]

}

FOOD_PRODUCTS = {

"Coffee": [

    {
        "name_en": "Premium Arabica Coffee",
        "name_ar": "قهوة أرابيكا",
        "name_fr": "Café Arabica",
        "price": 1200,

        "attributes": {
            "WEIGHT": [
                ("250g","250 غ","250g",0),
                ("500g","500 غ","500g",800),
            ]
        }
    },

    {
        "name_en": "Instant Coffee Mix",
        "name_ar": "قهوة سريعة",
        "name_fr": "Café Instantané",
        "price": 800,

        "attributes": {
            "WEIGHT": [
                ("100g","100 غ","100g",0)
            ]
        }
    },

    {
        "name_en": "Espresso Blend",
        "name_ar": "إسبريسو",
        "name_fr": "Espresso",
        "price": 1500,

        "attributes": {
            "WEIGHT": [
                ("250g","250 غ","250g",0)
            ]
        }
    }
],

"Sweets": [

    {
        "name_en": "Chocolate Box Deluxe",
        "name_ar": "علبة شوكولاتة",
        "name_fr": "Boîte Chocolat",
        "price": 1800,
        "attributes": {}
    },

    {
        "name_en": "Algerian Baklava",
        "name_ar": "بقلاوة",
        "name_fr": "Baklava",
        "price": 1200,
        "attributes": {}
    },

    {
        "name_en": "Candy Mix Pack",
        "name_ar": "حلويات مشكلة",
        "name_fr": "Bonbons Mix",
        "price": 900,
        "attributes": {}
    }
]

}

CARS_PRODUCTS = {

"Car Accessories": [

    {
        "name_en": "Car Vacuum Cleaner",
        "name_ar": "مكنسة سيارة",
        "name_fr": "Aspirateur Auto",
        "price": 3200,
        "attributes": {}
    },

    {
        "name_en": "LED Headlights",
        "name_ar": "أضواء LED",
        "name_fr": "Phares LED",
        "price": 4500,
        "attributes": {
            "COLOR": [
                ("White","أبيض","Blanc","#FFFFFF",0),
                ("Blue","أزرق","Bleu","#0066CC",500),
            ]
        }
    },

    {
        "name_en": "Car Seat Cover",
        "name_ar": "غطاء مقاعد",
        "name_fr": "Housse Siège",
        "price": 6000,
        "attributes": {
            "COLOR": [
                ("Black","أسود","Noir","#000000",0),
                ("Red","أحمر","Rouge","#FF0000",800),
            ]
        }
    }
]

}

KIDS_PRODUCTS = {

"Toys": [

    {
        "name_en": "Remote Control Car",
        "name_ar": "سيارة تحكم",
        "name_fr": "Voiture Télécommandée",
        "price": 2800,
        "attributes": {}
    },

    {
        "name_en": "Educational Blocks",
        "name_ar": "مكعبات تعليمية",
        "name_fr": "Blocs Éducatifs",
        "price": 1500,
        "attributes": {}
    },

    {
        "name_en": "Plush Teddy Bear",
        "name_ar": "دب محشو",
        "name_fr": "Ours en Peluche",
        "price": 1800,
        "attributes": {}
    }
]

}

SERVICES_PRODUCTS = {

    "Photography": [

        {
            "name_en": "Event Photography",
            "name_ar": "تصوير حفلات",
            "name_fr": "Photographie Événements",
            "price": 15000,

            "attributes": {

                "Duration": [
                    {"value": "1 Hour", "extra_price": 0},
                    {"value": "2 Hours", "extra_price": 5000},
                    {"value": "4 Hours", "extra_price": 12000},
                    {"value": "Full Day", "extra_price": 25000}
                ],

                "Delivery Speed": [
                    {"value": "72 Hours", "extra_price": 0},
                    {"value": "48 Hours", "extra_price": 2000},
                    {"value": "24 Hours", "extra_price": 5000}
                ]
            }
        },

        {
            "name_en": "Product Photography",
            "name_ar": "تصوير منتجات",
            "name_fr": "Photographie Produit",
            "price": 12000,

            "attributes": {

                "Editing": [
                    {"value": "Basic", "extra_price": 0},
                    {"value": "Professional", "extra_price": 3000},
                    {"value": "Premium", "extra_price": 7000}
                ],

                "Background": [
                    {"value": "Standard", "extra_price": 0},
                    {"value": "Custom", "extra_price": 3000},
                    {"value": "Luxury", "extra_price": 7000}
                ]
            }
        }
    ],

    "Marketing": [

        {
            "name_en": "Social Media Campaign",
            "name_ar": "حملة تسويقية",
            "name_fr": "Campagne Marketing",
            "price": 20000,

            "attributes": {

                "Platform": [
                    {"value": "Facebook", "extra_price": 0},
                    {"value": "Instagram", "extra_price": 2000},
                    {"value": "TikTok", "extra_price": 3000},
                    {"value": "LinkedIn", "extra_price": 4000}
                ],

                "Campaign Duration": [
                    {"value": "7 Days", "extra_price": 0},
                    {"value": "15 Days", "extra_price": 8000},
                    {"value": "30 Days", "extra_price": 15000}
                ]
            }
        },

        {
            "name_en": "SEO Optimization",
            "name_ar": "تهيئة محركات البحث",
            "name_fr": "Optimisation SEO",
            "price": 25000,

            "attributes": {

                "Website Size": [
                    {"value": "Small Website", "extra_price": 0},
                    {"value": "Medium Website", "extra_price": 10000},
                    {"value": "Large Website", "extra_price": 25000}
                ],

                "Support Period": [
                    {"value": "1 Month", "extra_price": 0},
                    {"value": "3 Months", "extra_price": 8000},
                    {"value": "6 Months", "extra_price": 15000}
                ]
            }
        }
    ],

    "Design": [

        {
            "name_en": "Logo Design",
            "name_ar": "تصميم شعار",
            "name_fr": "Création de Logo",
            "price": 12000,

            "attributes": {

                "Concept Quality": [
                    {"value": "Basic", "extra_price": 0},
                    {"value": "Professional", "extra_price": 5000},
                    {"value": "Premium", "extra_price": 10000}
                ],

                "Revision Package": [
                    {"value": "2 Revisions", "extra_price": 0},
                    {"value": "5 Revisions", "extra_price": 3000},
                    {"value": "Unlimited", "extra_price": 7000}
                ]
            }
        },

        {
            "name_en": "Brand Identity Design",
            "name_ar": "تصميم هوية بصرية",
            "name_fr": "Identité Visuelle",
            "price": 35000,

            "attributes": {

                "Package": [
                    {"value": "Basic", "extra_price": 0},
                    {"value": "Professional", "extra_price": 15000},
                    {"value": "Premium", "extra_price": 30000}
                ]
            }
        },

        {
            "name_en": "Social Media Post Design",
            "name_ar": "تصميم منشورات التواصل",
            "name_fr": "Design Réseaux Sociaux",
            "price": 5000,

            "attributes": {

                "Design Level": [
                    {"value": "Basic", "extra_price": 0},
                    {"value": "Professional", "extra_price": 2000},
                    {"value": "Premium", "extra_price": 5000}
                ]
            }
        }
    ],

    "Programming": [

        {
            "name_en": "Business Website Development",
            "name_ar": "تطوير موقع شركة",
            "name_fr": "Développement Site Web",
            "price": 60000,

            "attributes": {

                "Website Type": [
                    {"value": "Landing Page", "extra_price": 0},
                    {"value": "Corporate Website", "extra_price": 30000},
                    {"value": "Custom Platform", "extra_price": 80000}
                ],

                "Languages": [
                    {"value": "Arabic", "extra_price": 0},
                    {"value": "French", "extra_price": 5000},
                    {"value": "English", "extra_price": 5000},
                    {"value": "Multilingual", "extra_price": 15000}
                ]
            }
        },

        {
            "name_en": "E-Commerce Store Development",
            "name_ar": "تطوير متجر إلكتروني",
            "name_fr": "Développement Boutique E-commerce",
            "price": 90000,

            "attributes": {

                "Payment Integration": [
                    {"value": "Cash Only", "extra_price": 0},
                    {"value": "BaridiMob", "extra_price": 5000},
                    {"value": "CIB", "extra_price": 10000},
                    {"value": "All Methods", "extra_price": 15000}
                ],

                "Store Level": [
                    {"value": "Starter", "extra_price": 0},
                    {"value": "Professional", "extra_price": 25000},
                    {"value": "Enterprise", "extra_price": 60000}
                ]
            }
        },

        {
            "name_en": "Mobile App Development",
            "name_ar": "تطوير تطبيق جوال",
            "name_fr": "Développement Application Mobile",
            "price": 250000,

            "attributes": {

                "Platform": [
                    {"value": "Android", "extra_price": 0},
                    {"value": "iOS", "extra_price": 50000},
                    {"value": "Android & iOS", "extra_price": 100000}
                ],

                "Complexity": [
                    {"value": "Basic", "extra_price": 0},
                    {"value": "Professional", "extra_price": 100000},
                    {"value": "Enterprise", "extra_price": 250000}
                ]
            }
        }
    ]
}

class Command1(BaseCommand):
    help = "Seed full marketplace products with variants"

    def handle(self, *args, **kwargs):

        self.stdout.write("Deleting old products...")

        # ProductVariant.objects.all().delete()
        # ProductAttribute.objects.all().delete()
        # Product.objects.all().delete()

        # ⚠️ keep stores/categories if you want, or uncomment:
        # ProductCategory.objects.all().delete()
        # StoreCategory.objects.all().delete()

        # =========================================================
        # 1. HELPERS
        # =========================================================

        def create_attr(category, en, ar, fr, color=None):
            return ProductAttribute.objects.create(
                category=category,
                value_en=en,
                value_ar=ar,
                value_fr=fr,
                color_code=color
            )

        def build_attributes(product, attributes_dict):
            """
            Convert dict -> real ProductAttribute objects
            """
            attr_map = {}

            for cat, values in attributes_dict.items():
                attr_map[cat] = []

                for v in values:
                    # v format: (en, ar, fr, price_add?, color?)
                    en, ar, fr = v[0], v[1], v[2]

                    extra_price = 0
                    color = None

                    if len(v) == 5:
                        color = v[3] if cat == "COLOR" else None
                        extra_price = v[4]
                    elif len(v) == 4:
                        extra_price = v[3]

                    attr = create_attr(cat, en, ar, fr, color)
                    attr.extra_price = extra_price

                    attr_map[cat].append(attr)

            return attr_map

        def generate_variants(product, attr_map):
            """
            Generate all combinations of attributes
            """

            keys = list(attr_map.keys())
            values = list(attr_map.values())

            for combo in itertools.product(*values):

                combo_attrs = list(combo)

                extra_price = sum(
                    getattr(a, "extra_price", 0) for a in combo_attrs
                )

                ProductVariant.objects.create(
                    product=product,
                    price_override=product.base_price + Decimal(extra_price),
                    stock=50,
                ).attribute_values.set(combo_attrs)

        # =========================================================
        # 2. LOAD YOUR DATA
        # =========================================================

        ALL_DATA = {
            "Fashion": FASHION_PRODUCTS,
            "Electronics": ELECTRONICS_PRODUCTS,
            "Home & Kitchen":HOME_KITCHEN_PRODUCTS,
            "Food":FOOD_PRODUCTS,
            "Cars":CARS_PRODUCTS,
            "Kids":KIDS_PRODUCTS,
            "Services":SERVICES_PRODUCTS
        }

        # =========================================================
        # 3. MAIN SEED
        # =========================================================

        for store_category_name, categories_data in ALL_DATA.items():

            store_category = StoreCategory.objects.get(
                name_en=store_category_name
            )

            # loop product categories
            for product_cat_name, products in categories_data.items():

                product_category = ProductCategory.objects.get(
                    store_category=store_category,
                    name_en=product_cat_name
                )

                # pick any store (demo purpose)
                store = Store.objects.filter(
                    categories=store_category
                ).first()

                if not store:
                    continue

                for p in products:

                    product = Product.objects.create(
                        store=store,
                        category=product_category,
                        name_en=p["name_en"],
                        name_ar=p["name_ar"],
                        name_fr=p["name_fr"],
                        description_en=p.get("description_en", ""),
                        description_ar=p.get("description_ar", ""),
                        description_fr=p.get("description_fr", ""),
                        base_price=Decimal(p["price"]),
                        is_active=True,
                        is_featured=True,
                        is_new_arrival=True,
                    )

                    attr_map = build_attributes(
                        product,
                        p.get("attributes", {})
                    )

                    generate_variants(product, attr_map)

                    self.stdout.write(
                        f"Created: {product.name_en}"
                    )

        self.stdout.write(self.style.SUCCESS("Seeding completed!"))


import itertools

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from stores.models import (
    Store,
    StoreCategory,
    ProductCategory,
    Product,
    ProductAttribute,
    ProductVariant,
)



class Command(BaseCommand):

    help = "Seed marketplace products"

    def handle(self, *args, **kwargs):

        self.stdout.write("Starting seed...")

        # --------------------------------------------------
        # Helpers
        # --------------------------------------------------

        def create_attribute(label, value_data):

            value = value_data["value"]
            extra_price = Decimal(
                str(
                    value_data.get(
                        "extra_price",
                        0
                    )
                )
            )

            attr, created = ProductAttribute.objects.get_or_create(

                category=ProductAttribute.Category.OTHER,

                label_en=label,
                label_ar=label,
                label_fr=label,

                value_en=value,
                value_ar=value,
                value_fr=value,
            )

            attr.extra_price = extra_price

            return attr

        def build_attributes(attributes_dict):

            attr_map = {}

            for label, values in attributes_dict.items():

                attr_map[label] = []

                for value_data in values:

                    try:

                        attr = create_attribute(
                            label,
                            value_data
                        )

                        attr_map[label].append(attr)

                    except Exception as e:

                        self.stdout.write(
                            self.style.WARNING(
                                f"Attribute error: {e}"
                            )
                        )

            return attr_map

        def generate_variants(product, attr_map):

            try:

                if not attr_map:

                    ProductVariant.objects.get_or_create(
                        product=product,
                        stock=50,
                        defaults={
                            "price_override": product.base_price
                        }
                    )

                    return

                combinations = itertools.product(
                    *attr_map.values()
                )

                for combo in combinations:

                    combo_attrs = list(combo)

                    extra_price = sum(
                        getattr(
                            attr,
                            "extra_price",
                            0
                        )
                        for attr in combo_attrs
                    )

                    variant = ProductVariant.objects.create(

                        product=product,

                        stock=50,

                        price_override=(
                            product.base_price
                            + Decimal(extra_price)
                        )
                    )

                    variant.attribute_values.set(
                        combo_attrs
                    )

            except Exception as e:

                self.stdout.write(
                    self.style.ERROR(
                        f"Variant error for "
                        f"{product.name_en}: {e}"
                    )
                )

        # --------------------------------------------------
        # DATA
        # --------------------------------------------------

        ALL_DATA = {
            "Services": SERVICES_PRODUCTS
        }

        # --------------------------------------------------
        # MAIN LOOP
        # --------------------------------------------------

        for store_category_name, categories_data in ALL_DATA.items():

            try:

                store_category = StoreCategory.objects.get(
                    name_en=store_category_name
                )

            except StoreCategory.DoesNotExist:

                self.stdout.write(
                    self.style.ERROR(
                        f"Store category not found: "
                        f"{store_category_name}"
                    )
                )

                continue

            for category_name, products in categories_data.items():

                try:

                    product_category = ProductCategory.objects.get(
                        store_category=store_category,
                        name_en=category_name
                    )

                except ProductCategory.DoesNotExist:

                    self.stdout.write(
                        self.style.WARNING(
                            f"Missing category: "
                            f"{category_name}"
                        )
                    )

                    continue

                store = Store.objects.filter(
                    categories=store_category
                ).first()

                if not store:

                    self.stdout.write(
                        self.style.WARNING(
                            f"No store found for "
                            f"{store_category_name}"
                        )
                    )

                    continue

                for product_data in products:

                    try:

                        with transaction.atomic():

                            product = Product.objects.create(

                                store=store,

                                category=product_category,

                                name_en=product_data["name_en"],
                                name_ar=product_data["name_ar"],
                                name_fr=product_data["name_fr"],

                                description_en=product_data.get(
                                    "description_en",
                                    ""
                                ),

                                description_ar=product_data.get(
                                    "description_ar",
                                    ""
                                ),

                                description_fr=product_data.get(
                                    "description_fr",
                                    ""
                                ),

                                base_price=Decimal(
                                    str(
                                        product_data["price"]
                                    )
                                ),

                                is_active=True,
                                is_featured=True,
                                is_new_arrival=True,
                            )

                            attr_map = build_attributes(
                                product_data.get(
                                    "attributes",
                                    {}
                                )
                            )

                            generate_variants(
                                product,
                                attr_map
                            )

                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"Created: "
                                    f"{product.name_en}"
                                )
                            )

                    except Exception as e:

                        self.stdout.write(
                            self.style.ERROR(
                                f"Failed product "
                                f"{product_data.get('name_en')} "
                                f"-> {e}"
                            )
                        )

        self.stdout.write(
            self.style.SUCCESS(
                "Seeding completed successfully."
            )
        )
