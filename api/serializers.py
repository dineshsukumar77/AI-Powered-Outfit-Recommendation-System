from rest_framework import serializers
from .models import Wardrobe, WardrobeItem


class WardrobeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WardrobeItem
        fields = ['id', 'name', 'category', 'description', 'color', 'created_at']


class WardrobeItemWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = WardrobeItem
        fields = ['name', 'category', 'description', 'color']


class WardrobeSerializer(serializers.ModelSerializer):
    items = WardrobeItemSerializer(many=True, read_only=True)

    class Meta:
        model = Wardrobe
        fields = ['id', 'name', 'items', 'created_at', 'updated_at']


class WardrobeListSerializer(serializers.ModelSerializer):
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Wardrobe
        fields = ['id', 'name', 'item_count', 'created_at', 'updated_at']

    def get_item_count(self, obj):
        return obj.items.count()
