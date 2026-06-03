from django.core.management.base import BaseCommand
from accounts.models import User
from studio.models import Testimonial


class Command(BaseCommand):
    help = "Seed testimonials"

    def handle(self, *args, **kwargs):

        Testimonial.objects.all().delete()

        users_data = [
            {
                "username": "sarah",
                "first_name": "Sarah",
                "last_name": "Jenkins",
                "email": "sarah@example.com",
            },
            {
                "username": "david",
                "first_name": "David",
                "last_name": "Chen",
                "email": "david@example.com",
            },
            {
                "username": "marcus",
                "first_name": "Marcus",
                "last_name": "Thorne",
                "email": "marcus@example.com",
            }
        ]

        testimonials = [
            {
                "feedback": "MarketShot transformed our brand's visual language completely. Our conversion rates increased by 40% after our first UGC campaign.",
                "rating": 5
            },
            {
                "feedback": "The studio facilities are unmatched. It's truly a one-stop-shop for everything creative and marketing related.",
                "rating": 5
            },
            {
                "feedback": "Their data-driven approach to marketing combined with world-class production is exactly what we were looking for.",
                "rating": 5
            }
        ]

        for user_data, testimonial_data in zip(users_data, testimonials):

            user, created = User.objects.get_or_create(
                username=user_data["username"],
                defaults={
                    "first_name": user_data["first_name"],
                    "last_name": user_data["last_name"],
                    "email": user_data["email"],
                }
            )

            user.set_password("123456")
            user.save()

            Testimonial.objects.create(
                client=user,
                feedback=testimonial_data["feedback"],
                rating=testimonial_data["rating"],
                is_active=True
            )

        self.stdout.write(
            self.style.SUCCESS("Testimonials seeded successfully")
        )