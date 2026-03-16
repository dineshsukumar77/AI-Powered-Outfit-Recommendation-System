"""
Wardrobe and item models for saving user's clothes.
"""
from django.db import models


class UserAccount(models.Model):
    """Login account: username + hashed password, stored in MySQL."""
    username = models.CharField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['username']

    def __str__(self) -> str:
        return self.username


class Person(models.Model):
    """Person profile tied to a user account and their wardrobes/outfits."""
    name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Wardrobe(models.Model):
    """A saved wardrobe (collection of items) belonging to a person."""
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name='wardrobes', null=True, blank=True
    )
    name = models.CharField(max_length=200, default='My Wardrobe')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.name


class WardrobeItem(models.Model):
    """A single clothing item in a wardrobe."""
    CATEGORY_CHOICES = [
        ('top', 'Top'),
        ('bottom', 'Bottom'),
        ('outerwear', 'Outerwear'),
        ('shoes', 'Shoes'),
        ('accessory', 'Accessory'),
        ('dress', 'Dress'),
        ('other', 'Other'),
    ]

    wardrobe = models.ForeignKey(Wardrobe, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    description = models.TextField(blank=True)  # e.g. "Navy blazer, wool"
    color = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class OutfitRecord(models.Model):
    """Stores an outfit recommendation for a person."""

    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='outfit_records')
    wardrobe = models.ForeignKey(Wardrobe, on_delete=models.SET_NULL, null=True, blank=True, related_name='outfit_records')
    occasion = models.CharField(max_length=255)
    weather = models.CharField(max_length=255)
    style_preference = models.CharField(max_length=100)
    outfits = models.JSONField()  # list of outfits from LLM
    suggested_purchase = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.person.name} · {self.occasion} · {self.created_at:%Y-%m-%d}"
