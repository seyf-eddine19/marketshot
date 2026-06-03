from django.core.management.base import BaseCommand
from studio.models import Project


class Command(BaseCommand):
    help = "Seed portfolio projects"

    def handle(self, *args, **kwargs):

        Project.objects.all().delete()

        projects = [

            {
                "title_ar": "حملة لوكس هورايزن",
                "title_en": "Luxe Horizon Campaign",
                "title_fr": "Campagne Luxe Horizon",

                "description_ar": "حملة تصوير احترافية للعلامات التجارية الفاخرة تضمنت تصوير منتجات ومحتوى إعلاني عالي الجودة.",
                "description_en": "Professional campaign for luxury brands including product photography and high-end promotional content.",
                "description_fr": "Campagne professionnelle pour marques de luxe comprenant photographie produit et contenu promotionnel."
            },

            {
                "title_ar": "هوية سوشال إيكو",
                "title_en": "Social Echo Brand Kit",
                "title_fr": "Kit de Marque Social Echo",

                "description_ar": "تصميم هوية بصرية متكاملة ومحتوى تسويقي لمنصة رقمية حديثة.",
                "description_en": "Complete visual identity and marketing content for a modern digital platform.",
                "description_fr": "Identité visuelle complète et contenu marketing pour une plateforme numérique moderne."
            },

            {
                "title_ar": "سلسلة أوربان فلو",
                "title_en": "Urban Flow Series",
                "title_fr": "Série Urban Flow",

                "description_ar": "إنتاج فيديوهات إبداعية قصيرة مخصصة لمنصات التواصل الاجتماعي.",
                "description_en": "Creative short-form video production optimized for social media platforms.",
                "description_fr": "Production vidéo créative courte optimisée pour les réseaux sociaux."
            },

            {
                "title_ar": "مسرع النمو 2.0",
                "title_en": "Growth Accelerator 2.0",
                "title_fr": "Accélérateur de Croissance 2.0",

                "description_ar": "استراتيجية تسويق رقمي شاملة أدت إلى زيادة التفاعل والمبيعات.",
                "description_en": "Comprehensive digital marketing strategy that increased engagement and sales.",
                "description_fr": "Stratégie marketing numérique complète augmentant l'engagement et les ventes."
            },

            {
                "title_ar": "جلسة تصوير مطعم",
                "title_en": "Restaurant Showcase",
                "title_fr": "Présentation Restaurant",

                "description_ar": "تصوير احترافي للأطعمة والمساحات الداخلية للمطاعم.",
                "description_en": "Professional photography for food and restaurant interiors.",
                "description_fr": "Photographie professionnelle pour nourriture et intérieurs de restaurant."
            },

            {
                "title_ar": "عرض عقاري فاخر",
                "title_en": "Luxury Real Estate",
                "title_fr": "Immobilier de Luxe",

                "description_ar": "تصوير وإنتاج فيديو للعقارات الفاخرة والمساحات التجارية.",
                "description_en": "Photography and video production for luxury properties and commercial spaces.",
                "description_fr": "Photographie et production vidéo pour propriétés de luxe."
            },
            {
                "title_ar": "حملة لوكس هورايزن",
                "title_en": "Luxe Horizon Campaign",
                "title_fr": "Campagne Luxe Horizon",

                "description_ar": "مشروع تصوير احترافي لعلامة فاخرة.",
                "description_en": "High-end photography campaign for a luxury brand.",
                "description_fr": "Campagne photo haut de gamme pour une marque de luxe.",
            }

        ]

        for index, project in enumerate(projects):
            Project.objects.create(**project)

        self.stdout.write(
            self.style.SUCCESS(
                "Projects seeded successfully"
            )
        )