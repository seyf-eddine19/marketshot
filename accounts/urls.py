
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path("password/change/", views.CustomPasswordChangeView.as_view(), name="change_password"),
    path("password/done/", views.CustomPasswordChangeDoneView.as_view(), name="password_change_done"),
]