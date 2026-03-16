from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from api.models import Person, UserAccount, Wardrobe, WardrobeItem


class Command(BaseCommand):
    help = "Create a Demo user (login: Demo / style123), their Person, and Sample Wardrobe with sample items."

    def handle(self, *args, **options):
        UserAccount.objects.get_or_create(
            username="Demo",
            defaults={"password_hash": make_password("style123")},
        )
        person, _ = Person.objects.get_or_create(name="Demo")
        wardrobe, created = Wardrobe.objects.get_or_create(
            person=person, name="Sample Wardrobe", defaults={"person": person}
        )
        if not created:
            wardrobe.person = person
            wardrobe.save()
            wardrobe.items.all().delete()

        items = [
            # Tops
            {"name": "White crew‑neck t‑shirt", "category": "top", "description": "Cotton basic tee", "color": "White"},
            {"name": "Light blue oxford shirt", "category": "top", "description": "Button‑down, slim fit", "color": "Light blue"},
            {"name": "Black turtleneck sweater", "category": "top", "description": "Fine knit, fitted", "color": "Black"},
            # Bottoms
            {"name": "Dark wash slim jeans", "category": "bottom", "description": "Non‑distressed denim", "color": "Indigo"},
            {"name": "Charcoal wool trousers", "category": "bottom", "description": "Tailored, ankle length", "color": "Charcoal"},
            {"name": "Beige chinos", "category": "bottom", "description": "Casual straight fit", "color": "Beige"},
            # Outerwear
            {"name": "Navy blazer", "category": "outerwear", "description": "Unstructured, casual‑smart", "color": "Navy"},
            {"name": "Camel overcoat", "category": "outerwear", "description": "Wool coat, mid‑length", "color": "Camel"},
            {"name": "Black leather biker jacket", "category": "outerwear", "description": "Cropped moto style", "color": "Black"},
            # Shoes
            {"name": "White leather sneakers", "category": "shoes", "description": "Minimal, low‑top", "color": "White"},
            {"name": "Brown leather loafers", "category": "shoes", "description": "Penny loafers", "color": "Brown"},
            {"name": "Black derby shoes", "category": "shoes", "description": "Polished, formal", "color": "Black"},
            # Accessories
            {"name": "Brown leather belt", "category": "accessory", "description": "Matches brown shoes", "color": "Brown"},
            {"name": "Black leather belt", "category": "accessory", "description": "Matches black shoes", "color": "Black"},
            {"name": "Silver dress watch", "category": "accessory", "description": "Metal bracelet", "color": "Silver"},
            {"name": "Navy knitted tie", "category": "accessory", "description": "Casual‑smart texture", "color": "Navy"},
            # Dresses / other
            {"name": "Black slip dress", "category": "dress", "description": "Midi length, satin finish", "color": "Black"},
            {"name": "Floral wrap dress", "category": "dress", "description": "Soft print, V‑neck", "color": "Navy / floral"},
        ]

        WardrobeItem.objects.bulk_create(
            [WardrobeItem(wardrobe=wardrobe, **item) for item in items]
        )

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(items)} items into '{wardrobe.name}'"))

