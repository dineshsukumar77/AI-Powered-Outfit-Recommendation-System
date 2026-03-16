"""
API views: wardrobe CRUD, recommend, weather.
"""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from django.contrib.auth.hashers import make_password, check_password
from django.db import transaction

from .models import Wardrobe, WardrobeItem, Person, OutfitRecord, UserAccount
from .serializers import (
    WardrobeSerializer,
    WardrobeListSerializer,
    WardrobeItemSerializer,
    WardrobeItemWriteSerializer,
)
from .services import get_outfit_recommendations, get_weather_for_location
from .services.image_extract import ImageExtractionError, extract_wardrobe_from_image


@api_view(['GET', 'POST'])
def wardrobe_list(request: Request):
    if request.method == 'GET':
        person_name = request.query_params.get('person_name', '').strip()
        if not person_name:
            return Response([])
        person = Person.objects.filter(name=person_name).first()
        if not person:
            return Response([])
        wardrobes = Wardrobe.objects.filter(person=person)
        serializer = WardrobeListSerializer(wardrobes, many=True)
        return Response(serializer.data)
    # POST: create new wardrobe for the given person
    data = request.data or {}
    person_name = (data.get('person_name') or '').strip()
    if not person_name:
        return Response(
            {'detail': 'person_name is required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    person, _ = Person.objects.get_or_create(name=person_name)
    serializer = WardrobeSerializer(data={'name': data.get('name', 'My Wardrobe')})
    if serializer.is_valid():
        serializer.save(person=person)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def _get_wardrobe_for_person(pk: int, person_name: str):
    """Return wardrobe only if it belongs to the given person."""
    if not person_name:
        return None, None
    person = Person.objects.filter(name=person_name).first()
    if not person:
        return None, None
    try:
        wardrobe = Wardrobe.objects.get(pk=pk, person=person)
        return wardrobe, person
    except Wardrobe.DoesNotExist:
        return None, None


def _serialize_wardrobe_item(item: WardrobeItem) -> dict:
    return {
        'id': item.id,
        'name': item.name,
        'category': item.category,
        'description': item.description,
        'color': item.color,
        'created_at': item.created_at,
    }


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def wardrobe_detail(request: Request, pk: int):
    person_name = request.query_params.get('person_name', '').strip()
    wardrobe, _ = _get_wardrobe_for_person(pk, person_name)
    if not wardrobe:
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = WardrobeSerializer(wardrobe)
        return Response(serializer.data)
    if request.method in ('PUT', 'PATCH'):
        serializer = WardrobeSerializer(wardrobe, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        wardrobe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'POST'])
def wardrobe_items(request: Request, wardrobe_pk: int):
    person_name = request.query_params.get('person_name', '').strip()
    wardrobe, _ = _get_wardrobe_for_person(wardrobe_pk, person_name)
    if not wardrobe:
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        items = wardrobe.items.all()
        serializer = WardrobeItemSerializer(items, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        serializer = WardrobeItemWriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(wardrobe=wardrobe)
            return Response(WardrobeItemSerializer(serializer.instance).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['PUT', 'PATCH', 'DELETE'])
def wardrobe_item_detail(request: Request, wardrobe_pk: int, item_pk: int):
    person_name = request.query_params.get('person_name', '').strip()
    wardrobe, _ = _get_wardrobe_for_person(wardrobe_pk, person_name)
    if not wardrobe:
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
    try:
        item = WardrobeItem.objects.get(wardrobe_id=wardrobe_pk, pk=item_pk)
    except WardrobeItem.DoesNotExist:
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method in ('PUT', 'PATCH'):
        serializer = WardrobeItemWriteSerializer(item, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(WardrobeItemSerializer(serializer.instance).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
def recommend(request: Request):
    """
    Body: {
      "wardrobe_items": [{"name","category","description","color"}],  // or use "wardrobe_id" to load from DB
      "occasion": "...",
      "weather": "...",   // optional if weather_city provided
      "weather_city": "...",  // optional, fetches live weather
      "style_preference": "..."
    }
    """
    data = request.data
    user_name = (data.get('user_name') or '').strip()
    wardrobe_items = data.get('wardrobe_items')
    wardrobe_id = data.get('wardrobe_id')

    wardrobe = None
    if wardrobe_id and not wardrobe_items:
        try:
            wardrobe = Wardrobe.objects.get(pk=wardrobe_id)
            wardrobe_items = [
                {
                    'name': i.name,
                    'category': i.category,
                    'description': i.description,
                    'color': i.color,
                }
                for i in wardrobe.items.all()
            ]
        except Wardrobe.DoesNotExist:
            return Response({'detail': 'Wardrobe not found.'}, status=status.HTTP_404_NOT_FOUND)

    if not wardrobe_items:
        return Response(
            {'detail': 'Provide wardrobe_items or wardrobe_id.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    occasion = data.get('occasion', 'casual day')
    weather = data.get('weather', '')
    style = data.get('style_preference', 'casual')

    # Optional: fetch weather by city
    weather_city = data.get('weather_city', '').strip()
    if weather_city:
        weather = get_weather_for_location(city=weather_city) or weather

    if not weather:
        weather = 'Moderate temperature'

    result = get_outfit_recommendations(wardrobe_items, occasion, weather, style)

    # Persist the recommendation per person in MySQL (or current DB)
    person = None
    if user_name:
        person, _ = Person.objects.get_or_create(name=user_name)
    else:
        person, _ = Person.objects.get_or_create(name='Guest')

    OutfitRecord.objects.create(
        person=person,
        wardrobe=wardrobe,
        occasion=occasion,
        weather=weather,
        style_preference=style,
        outfits=result.get('outfits') or [],
        suggested_purchase=result.get('suggested_purchase') or '',
    )

    return Response(result)


@api_view(['GET'])
def weather(request: Request):
    """GET ?city=London or ?lat=40.7&lon=-74.0"""
    city = request.query_params.get('city', '').strip()
    lat = request.query_params.get('lat')
    lon = request.query_params.get('lon')
    if lat is not None:
        try:
            lat = float(lat)
        except (TypeError, ValueError):
            lat = None
    if lon is not None:
        try:
            lon = float(lon)
        except (TypeError, ValueError):
            lon = None

    description = get_weather_for_location(city=city or None, lat=lat, lon=lon)
    return Response({'weather': description})


@api_view(['POST'])
def register(request: Request):
    """
    Body: { "username": "...", "password": "..." }
    Creates user in MySQL and a Person so they have their own wardrobes/outfits.
    """
    data = request.data or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()

    if not username:
        return Response({'detail': 'Username is required.'}, status=status.HTTP_400_BAD_REQUEST)
    if not password:
        return Response({'detail': 'Password is required.'}, status=status.HTTP_400_BAD_REQUEST)
    if len(username) < 2:
        return Response({'detail': 'Username must be at least 2 characters.'}, status=status.HTTP_400_BAD_REQUEST)
    if len(password) < 4:
        return Response({'detail': 'Password must be at least 4 characters.'}, status=status.HTTP_400_BAD_REQUEST)

    if UserAccount.objects.filter(username__iexact=username).exists():
        return Response({'detail': 'That username is already taken.'}, status=status.HTTP_400_BAD_REQUEST)

    UserAccount.objects.create(username=username, password_hash=make_password(password))
    Person.objects.get_or_create(name=username)
    return Response({'username': username}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login(request: Request):
    """
    Body: { "username": "...", "password": "..." }
    Returns { "username": "..." } on success; 401 on invalid credentials.
    """
    data = request.data or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()

    if not username or not password:
        return Response({'detail': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    account = UserAccount.objects.filter(username__iexact=username).first()
    if not account or not check_password(password, account.password_hash):
        return Response({'detail': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)

    return Response({'username': account.username})


MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}


@api_view(['POST'])
def extract_wardrobe(request: Request):
    """
    POST multipart/form-data with field "image" (file).
    Optional fields:
      - person_name
      - wardrobe_id
    Returns extracted items and saves them to the user's wardrobe when person_name is provided.
    """
    image_file = request.FILES.get('image')
    if not image_file:
        return Response({'detail': 'No image file provided. Use form field "image".'}, status=status.HTTP_400_BAD_REQUEST)
    if image_file.size > MAX_IMAGE_SIZE:
        return Response({'detail': 'Image too large. Maximum size is 5MB.'}, status=status.HTTP_400_BAD_REQUEST)
    content_type = image_file.content_type or ''
    if content_type.split(';')[0].strip().lower() not in ALLOWED_IMAGE_TYPES:
        return Response({'detail': 'Invalid image type. Use JPEG, PNG, GIF, or WebP.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        image_bytes = image_file.read()
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    try:
        items = extract_wardrobe_from_image(image_bytes, content_type)
    except ImageExtractionError as exc:
        return Response(
            {'detail': str(exc)},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    if not items:
        return Response({'items': []})

    person_name = (request.data.get('person_name') or '').strip()
    wardrobe_id = (request.data.get('wardrobe_id') or '').strip()
    if not person_name:
        return Response({'items': items})

    person, _ = Person.objects.get_or_create(name=person_name)
    if wardrobe_id:
        wardrobe = Wardrobe.objects.filter(pk=wardrobe_id, person=person).first()
        if not wardrobe:
            return Response({'detail': 'Wardrobe not found.'}, status=status.HTTP_404_NOT_FOUND)
    else:
        wardrobe = Wardrobe.objects.create(person=person, name='Photo Upload Wardrobe')

    with transaction.atomic():
        for item in items:
            WardrobeItem.objects.create(
                wardrobe=wardrobe,
                name=item['name'],
                category=item['category'],
                description=item.get('description', ''),
                color=item.get('color', ''),
            )

    return Response({
        'items': [_serialize_wardrobe_item(item) for item in wardrobe.items.all()],
        'saved_count': len(items),
        'wardrobe': {
            'id': wardrobe.id,
            'name': wardrobe.name,
        },
    })
