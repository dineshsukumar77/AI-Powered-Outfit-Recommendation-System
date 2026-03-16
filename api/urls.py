from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register),
    path('login/', views.login),
    path('wardrobes/', views.wardrobe_list),
    path('wardrobes/<int:pk>/', views.wardrobe_detail),
    path('wardrobes/<int:wardrobe_pk>/items/', views.wardrobe_items),
    path('wardrobes/<int:wardrobe_pk>/items/<int:item_pk>/', views.wardrobe_item_detail),
    path('recommend/', views.recommend),
    path('weather/', views.weather),
    path('extract-wardrobe/', views.extract_wardrobe),
]
