from django.core.management.base import BaseCommand
from studio.models import Service

from django.core.management.base import BaseCommand
from studio.models import Service


class Command(BaseCommand):
    help = "Seed Services (AR/EN/FR)"

    def handle(self, *args, **kwargs):
        Service.objects.all().delete()  # Clean existing services
        self.stdout.write(self.style.SUCCESS("Existing services deleted successfully"))

        services = [

            {
                "icon": "photo_camera",
                "color_class": "primary",

                "title_en": "Photography",
                "title_ar": "التصوير الفوتوغرافي",
                "title_fr": "Photographie",

                "description_en": "Studio, product, food, real estate and commercial photography with high-end production quality.",
                "description_ar": "تصوير استوديو، منتجات، طعام، عقارات ومشاريع تجارية بجودة احترافية عالية.",
                "description_fr": "Photographie studio, produits, nourriture, immobilier et entreprises avec haute qualité.",

                "order": 1,
            },

            {
                "icon": "videocam",
                "color_class": "secondary",

                "title_en": "Video Production",
                "title_ar": "إنتاج الفيديو",
                "title_fr": "Production Vidéo",

                "description_en": "Promotional videos, ads, reels, cinematic content, and social media video production.",
                "description_ar": "إعلانات، ريلز، فيديوهات تسويقية ومحتوى سينمائي احترافي.",
                "description_fr": "Vidéos promotionnelles, publicités, reels et contenu cinématographique.",

                "order": 2,
            },

            {
                "icon": "diversity_3",
                "color_class": "primary",

                "title_en": "UGC Content",
                "title_ar": "محتوى UGC",
                "title_fr": "Contenu UGC",

                "description_en": "Authentic creator-driven content that increases trust, engagement, and conversions.",
                "description_ar": "محتوى حقيقي من صناع المحتوى لزيادة الثقة والمبيعات.",
                "description_fr": "Contenu authentique créé par les utilisateurs pour augmenter la confiance.",

                "order": 3,
            },

            {
                "icon": "trending_up",
                "color_class": "primary",

                "title_en": "Digital Marketing",
                "title_ar": "التسويق الرقمي",
                "title_fr": "Marketing Digital",

                "description_en": "Paid ads, social media management, strategy, and performance-driven campaigns.",
                "description_ar": "إعلانات ممولة، إدارة السوشيال ميديا، واستراتيجيات تسويق احترافية.",
                "description_fr": "Publicité payante, gestion des réseaux sociaux et stratégie marketing.",

                "order": 4,
            },

            {
                "icon": "brush",
                "color_class": "secondary",

                "title_en": "Design & Editing",
                "title_ar": "التصميم والمونتاج",
                "title_fr": "Design & Montage",

                "description_en": "Photo retouching, video editing, branding design, and social media creatives.",
                "description_ar": "تعديل الصور، مونتاج الفيديو، وتصميم الهوية البصرية.",
                "description_fr": "Retouche photo, montage vidéo et design graphique.",

                "order": 5,
            },

            {
                "icon": "mic",
                "color_class": "primary",

                "title_en": "Voice Over",
                "title_ar": "التعليق الصوتي",
                "title_fr": "Voix Off",

                "description_en": "Professional Arabic/French voice-over for ads, videos, and promotional content.",
                "description_ar": "تعليق صوتي احترافي بالعربية والفرنسية للإعلانات والفيديوهات.",
                "description_fr": "Voix off professionnelle en arabe et français.",

                "order": 6,
            },

            {
                "icon": "location_on",
                "color_class": "primary",

                "title_en": "On-Location Shooting",
                "title_ar": "التصوير الميداني",
                "title_fr": "Tournage sur site",

                "description_en": "Professional field photography and videography for restaurants, clinics, real estate, shops, and events directly at your location with full production setup.",
                "description_ar": "تصوير احترافي في موقع العميل (مطاعم، عيادات، محلات، عقارات، فعاليات).",
                "description_fr": "Tournage professionnel sur site pour restaurants, cliniques et entreprises.",

                "order": 7,
            },

            {
                "icon": "camera_indoor",
                "color_class": "secondary",

                "title_en": "Studio Rental",
                "title_ar": "كراء الاستوديو",
                "title_fr": "Location Studio",

                "description_en": "Fully equipped creative studio for hourly or daily rental for creators and businesses.",
                "description_ar": "استوديو مجهز للإيجار بالساعة أو اليوم لصناع المحتوى والشركات.",
                "description_fr": "Studio équipé à louer à l'heure ou à la journée.",

                "order": 8,
            },

            {
                "icon": "hub",
                "color_class": "primary",

                "title_en": "MarketShot Platform",
                "title_ar": "منصة MarketShot",
                "title_fr": "Plateforme MarketShot",

                "description_en": "A digital platform for booking services, managing content, and showcasing client products.",
                "description_ar": "منصة رقمية لحجز الخدمات وعرض المنتجات وإدارة المحتوى.",
                "description_fr": "Plateforme digitale pour réserver et gérer les services.",

                "order": 9,
            },

        ]

        for s in services:
            Service.objects.update_or_create(
                title_en=s["title_en"],
                defaults=s
            )

        self.stdout.write(self.style.SUCCESS("Clean services seeded successfully"))



        services = [
            {
                "icon": "photo_camera",
                "color_class": "primary",
                "title_ar": "التصوير الفوتوغرافي",
                "title_en": "Photography",
                "title_fr": "Photographie",
                "description_ar": "تصوير احترافي للمنتجات، المطاعم، العقارات والمشاريع التجارية.",
                "description_en": "High-end photography for products, restaurants, real estate and businesses.",
                "description_fr": "Photographie professionnelle pour produits, restaurants et entreprises.",
                "order": 1,
            },
            {
                "icon": "videocam",
                "color_class": "secondary",
                "title_ar": "إنتاج الفيديو",
                "title_en": "Video Production",
                "title_fr": "Production Vidéo",
                "description_ar": "إعلانات، ريلز، فيديوهات تسويقية احترافية.",
                "description_en": "Ads, reels, and professional marketing videos.",
                "description_fr": "Publicités, reels et vidéos marketing professionnelles.",
                "order": 2,
            },
            {
                "icon": "location_on",
                "color_class": "primary",
                "title_ar": "التصوير الميداني",
                "title_en": "On-Location Shooting",
                "title_fr": "Tournage sur site",
                "description_ar": "تصوير احترافي في موقع العميل (مطاعم، عيادات، محلات...).",
                "description_en": "Professional shooting at client locations (restaurants, clinics, shops...).",
                "description_fr": "Tournage professionnel chez le client (restaurants, cliniques...).",
                "order": 3,
            },
            {
                "icon": "brush",
                "color_class": "secondary",
                "title_ar": "التصميم والمونتاج",
                "title_en": "Design & Editing",
                "title_fr": "Design & Montage",
                "description_ar": "تصميم، تعديل صور، مونتاج فيديو احترافي.",
                "description_en": "Photo editing, video editing, and design services.",
                "description_fr": "Retouche photo, montage vidéo et design.",
                "order": 4,
            },
            {
                "icon": "mic",
                "color_class": "primary",
                "title_ar": "التعليق الصوتي",
                "title_en": "Voice Over",
                "title_fr": "Voix Off",
                "description_ar": "تعليق صوتي عربي وفرنسي احترافي للإعلانات.",
                "description_en": "Professional Arabic & French voice-over for ads.",
                "description_fr": "Voix off professionnelle en arabe et français.",
                "order": 5,
            },
            {
                "icon": "camera_indoor",
                "color_class": "secondary",
                "title_ar": "استوديو للتأجير",
                "title_en": "Studio Rental",
                "title_fr": "Location Studio",
                "description_ar": "استوديو مجهز للإيجار بالساعة أو اليوم.",
                "description_en": "Fully equipped studio for hourly or daily rental.",
                "description_fr": "Studio équipé à louer à l'heure ou à la journée.",
                "order": 6,
            },
        ]

        for s in services:
            Service.objects.update_or_create(
                title_en=s["title_en"],
                defaults=s
            )

        self.stdout.write(self.style.SUCCESS("Services seeded successfully"))