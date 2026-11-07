from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('parking/', views.facilities_view, name='facilities'),
    path('parking/<slug:slug>/', views.facility_detail_view, name='facility_detail'),
    path('book/', views.booking_checkout_view, name='booking_checkout'),
    path('booking/<str:reference>/', views.booking_confirmation_view, name='booking_confirmation'),
    path('booking/<str:reference>/cancel/', views.booking_cancel_view, name='booking_cancel'),
    path('verify-ticket/', views.verify_ticket_view, name='verify_ticket'),
    path('verify-ticket/<str:reference>/', views.verify_ticket_view, name='verify_ticket_ref'),
    path('favorite/<int:facility_id>/', views.toggle_favorite_view, name='toggle_favorite'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin-portal/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-portal/login/', views.admin_login_view, name='admin_login'),
    path('admin-portal/logout/', views.admin_logout_view, name='admin_logout'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]
