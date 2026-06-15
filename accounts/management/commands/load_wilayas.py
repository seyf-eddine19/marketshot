from django.core.management.base import BaseCommand
from accounts.models import Wilaya

# python manage.py load_wilayas
class Command(BaseCommand):
    help = "Load Algeria 58 Wilayas into database"

    def handle(self, *args, **kwargs):

        data = [
            (1, "Adrar", "أدرار", "Adrar"),
            (2, "Chlef", "الشلف", "Chlef"),
            (3, "Laghouat", "الأغواط", "Laghouat"),
            (4, "Oum El Bouaghi", "أم البواقي", "Oum El Bouaghi"),
            (5, "Batna", "باتنة", "Batna"),
            (6, "Béjaïa", "بجاية", "Béjaïa"),
            (7, "Biskra", "بسكرة", "Biskra"),
            (8, "Béchar", "بشار", "Béchar"),
            (9, "Blida", "البليدة", "Blida"),
            (10, "Bouira", "البويرة", "Bouira"),
            (11, "Tamanrasset", "تمنراست", "Tamanrasset"),
            (12, "Tébessa", "تبسة", "Tébessa"),
            (13, "Tlemcen", "تلمسان", "Tlemcen"),
            (14, "Tiaret", "تيارت", "Tiaret"),
            (15, "Tizi Ouzou", "تيزي وزو", "Tizi Ouzou"),
            (16, "Algiers", "الجزائر", "Algiers"),
            (17, "Djelfa", "الجلفة", "Djelfa"),
            (18, "Jijel", "جيجل", "Jijel"),
            (19, "Sétif", "سطيف", "Sétif"),
            (20, "Saïda", "سعيدة", "Saïda"),
            (21, "Skikda", "سكيكدة", "Skikda"),
            (22, "Sidi Bel Abbès", "سيدي بلعباس", "Sidi Bel Abbès"),
            (23, "Annaba", "عنابة", "Annaba"),
            (24, "Guelma", "قالمة", "Guelma"),
            (25, "Constantine", "قسنطينة", "Constantine"),
            (26, "Médéa", "المدية", "Médéa"),
            (27, "Mostaganem", "مستغانم", "Mostaganem"),
            (28, "M'Sila", "المسيلة", "M'Sila"),
            (29, "Mascara", "معسكر", "Mascara"),
            (30, "Ouargla", "ورقلة", "Ouargla"),
            (31, "Oran", "وهران", "Oran"),
            (32, "El Bayadh", "البيض", "El Bayadh"),
            (33, "Illizi", "إليزي", "Illizi"),
            (34, "Bordj Bou Arreridj", "برج بوعريريج", "Bordj Bou Arreridj"),
            (35, "Boumerdès", "بومرداس", "Boumerdès"),
            (36, "El Tarf", "الطارف", "El Tarf"),
            (37, "Tindouf", "تندوف", "Tindouf"),
            (38, "Tissemsilt", "تيسمسيلت", "Tissemsilt"),
            (39, "El Oued", "الوادي", "El Oued"),
            (40, "Khenchela", "خنشلة", "Khenchela"),
            (41, "Souk Ahras", "سوق أهراس", "Souk Ahras"),
            (42, "Tipaza", "تيبازة", "Tipaza"),
            (43, "Mila", "ميلة", "Mila"),
            (44, "Aïn Defla", "عين الدفلى", "Aïn Defla"),
            (45, "Naâma", "النعامة", "Naâma"),
            (46, "Aïn Témouchent", "عين تموشنت", "Aïn Témouchent"),
            (47, "Ghardaïa", "غرداية", "Ghardaïa"),
            (48, "Relizane", "غليزان", "Relizane"),

            # Newer administrative divisions (post-2019 reforms)
            (49, "Timimoun", "تيميمون", "Timimoun"),
            (50, "Bordj Badji Mokhtar", "برج باجي مختار", "Bordj Badji Mokhtar"),
            (51, "Ouled Djellal", "أولاد جلال", "Ouled Djellal"),
            (52, "Béni Abbès", "بني عباس", "Béni Abbès"),
            (53, "In Salah", "عين صالح", "In Salah"),
            (54, "In Guezzam", "عين قزام", "In Guezzam"),
            (55, "Touggourt", "تقرت", "Touggourt"),
            (56, "Djanet", "جانت", "Djanet"),
            (57, "El M'Ghair", "المغير", "El M'Ghair"),
            (58, "El Meniaa", "المنيعة", "El Meniaa"),

        ]

        created = 0
        updated = 0

        for code, en, ar, fr in data:
            obj, is_created = Wilaya.objects.update_or_create(
                code=code,
                defaults={
                    "name_en": en,
                    "name_ar": ar,
                    "name_fr": fr,
                }
            )

            if is_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"Wilayas loaded successfully ✔ Created: {created}, Updated: {updated}"
        ))