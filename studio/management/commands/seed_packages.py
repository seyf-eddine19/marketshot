from django.core.management.base import BaseCommand
from studio.models import Package, PackageFeature


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        PackageFeature.objects.all().delete()
        Package.objects.all().delete()

        # STARTER
        starter = Package.objects.create(
            title_en="Starter Spark",
            title_ar="البداية",
            title_fr="Starter",
            description_en="Perfect for small projects.",
            description_ar="مثالي للمشاريع الصغيرة",
            description_fr="Parfait pour les petits projets",
            base_price=1200,
            order=1,
            button_link="/booking?plan=starter"
        )

        PackageFeature.objects.bulk_create([
            PackageFeature(package=starter, text_en="10 Pro Product Photos", text_ar="10 صور احترافية", text_fr="10 photos pro", is_included=True),
            PackageFeature(package=starter, text_en="2 Social Media Clips (15s)", text_ar="2 فيديوهات قصيرة", text_fr="2 clips", is_included=True),
            PackageFeature(package=starter, text_en="Basic Ad Strategy Session", text_ar="استراتيجية إعلانات", text_fr="Stratégie", is_included=True),
            PackageFeature(package=starter, text_en="Priority Studio Access", text_ar="أولوية الاستوديو", text_fr="Accès prioritaire", is_included=False),
        ])

        # GROWTH
        growth = Package.objects.create(
            title_en="Growth Engine",
            title_ar="محرك النمو",
            title_fr="Croissance",
            description_en="Monthly creative & performance subscription.",
            description_ar="اشتراك شهري للنمو",
            description_fr="Abonnement mensuel",
            base_price=3500,
            discount=10,
            is_highlighted=True,
            order=2,
            button_link="/booking?plan=growth"
        )

        PackageFeature.objects.bulk_create([
            PackageFeature(package=growth, text_en="Monthly Photo & Video Drops", text_ar="محتوى شهري", text_fr="Contenu mensuel", is_included=True),
            PackageFeature(package=growth, text_en="Full Paid Ads Management", text_ar="إدارة الإعلانات", text_fr="Gestion ads", is_included=True),
            PackageFeature(package=growth, text_en="Dedicated Strategist", text_ar="استراتيجي خاص", text_fr="Stratège dédié", is_included=True),
            PackageFeature(package=growth, text_en="Priority Studio Bookings", text_ar="حجز أولوية", text_fr="Priorité studio", is_included=True),
            PackageFeature(package=growth, text_en="Reports", text_ar="تقارير", text_fr="Rapports", is_included=True),
        ])

        # ENTERPRISE
        enterprise = Package.objects.create(
            title_en="Enterprise Scale",
            title_ar="المؤسسات",
            title_fr="Entreprise",
            description_en="Custom white-glove production.",
            description_ar="حلول مخصصة",
            description_fr="Solutions sur mesure",
            base_price=0,
            order=3,
            button_link="/contact"
        )

        PackageFeature.objects.bulk_create([
            PackageFeature(package=enterprise, text_en="Full Production Team", text_ar="فريق كامل", text_fr="Équipe complète", is_included=True),
            PackageFeature(package=enterprise, text_en="Unlimited Studio Access", text_ar="استوديو غير محدود", text_fr="Studio illimité", is_included=True),
            PackageFeature(package=enterprise, text_en="International Campaigns", text_ar="حملات دولية", text_fr="Campagnes internationales", is_included=True),
            PackageFeature(package=enterprise, text_en="Custom CRM Dashboard", text_ar="لوحة مخصصة", text_fr="CRM personnalisé", is_included=True),
        ])

        self.stdout.write(self.style.SUCCESS("Packages seeded successfully"))