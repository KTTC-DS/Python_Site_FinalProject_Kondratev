from django.urls import path
from . import views


urlpatterns = [
    path('create/<int:ad_pk>/', views.create_rental_request, name='create_rental_request'),
    path('my/', views.my_rental_requests, name='my_rental_requests'),
    path('incoming/', views.incoming_rental_requests, name='incoming_rental_requests'),
    path('update/<int:pk>/<str:status>/', views.update_rental_request_status, name='update_rental_request_status'),
    path('pay/<int:rental_pk>/', views.mark_transaction_paid, name='mark_transaction_paid'),
]