from django.urls import path
from . import views, views_studio, views_accounts

app_name = 'dashboard'
urlpatterns = [
    # studio app
    path('', views_studio.DashboardView.as_view(), name='dashboard'),
    path('projects/', views_studio.ProjectListView.as_view(), name='project-list'),
    path('projects/add/', views_studio.ProjectCreateView.as_view(), name='project-add'),
    path('projects/<int:pk>/edit/', views_studio.ProjectUpdateView.as_view(), name='project-edit'),
    path('projects/<int:pk>/delete/', views_studio.ProjectDeleteView.as_view(), name='project-delete'),
    
    path('manage-services/', views_studio.ServiceManageView.as_view(), name='service-add'),
    path('manage-services/<int:pk>/', views_studio.ServiceManageView.as_view(), name='service-edit'),
    path('manage-services/<int:pk>/delete/', views_studio.ServiceDeleteView.as_view(), name='service-delete'),

    path('packages/', views_studio.PackageListView.as_view(), name='package-list'),
    path('packages/add/', views_studio.PackageCreateView.as_view(), name='package-add'),
    path('packages/<int:pk>/edit/', views_studio.PackageUpdateView.as_view(), name='package-edit'),
    path('packages/<int:pk>/delete/', views_studio.PackageDeleteView.as_view(), name='package-delete'), 

    path('testimonials/', views_studio.TestimonialListView.as_view(), name='testimonial-list'),

    path('contact-messages/', views_studio.ContactMessageListView.as_view(), name='contact-list'),
    path('contact-messages/<int:pk>/toggle-read/', views_studio.ContactMessageToggleReadView.as_view(), name='contact-toggle-read'),

    path('subscriptions/', views_studio.SubscriptionListView.as_view(), name='subscription-list'),

    path('bookings/', views_studio.BookingListView.as_view(), name='booking-list'),

    # stores app    
    path('manage-categories/', views.GlobalCategoryManageView.as_view(), name='manage-categories'),
    path('manage-categories/<int:pk>/', views.GlobalCategoryManageView.as_view(), name='manage-categories-detail'),

    path('stores/', views.StoreListView.as_view(), name='stores'),
    path('stores/add/', views.StoreCreateView.as_view(), name='store-add'),
    path('stores/<int:pk>/edit/', views.StoreUpdateView.as_view(), name='store-edit'),
    path('stores/<int:pk>/delete/', views.StoreDeleteView.as_view(), name='store-delete'),
    
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/add/', views.ProductCreateView.as_view(), name='product-add'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product-edit'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),

    path('ajax/attributes/', views.ajax_attributes_by_type, name='ajax-attributes-by-type'),

    # accounts app
    path('users/', views_accounts.UserListView.as_view(), name='user_list'),
    path('users/add/', views_accounts.UserCreateView.as_view(), name='user_add'),
    path('users/<int:pk>/edit/', views_accounts.UserUpdateView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', views_accounts.UserDeleteView.as_view(), name='user_delete'),
]