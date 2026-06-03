from django.urls import path
from . import views

app_name = 'studio'
urlpatterns = [
    path('', views.StudioHomeView.as_view(), name='home'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('booking/', views.BookingPageView.as_view(), name='booking'),
    path('booking/create/', views.BookingCreateView.as_view(), name='booking_create'),
]

