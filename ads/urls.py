from django.urls import path
from . import views



urlpatterns = [
    path('', views.ad_list, name='ad_list'),
    path('<int:pk>/', views.ad_detail, name='ad_detail'),
    path('create/', views.ad_create, name='ad_create'),
    path('<int:pk>/edit/', views.ad_edit, name='ad_edit'),
    path('<int:pk>/delete/', views.ad_delete, name='ad_delete'),
    path('moderation/', views.ad_moderation, name='ad_moderation'),
    path('my/', views.my_ads, name='my_ads'),
]