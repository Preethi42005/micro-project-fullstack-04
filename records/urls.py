from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    # Authentication URLs
    path('accounts/login/', auth_views.LoginView.as_view(template_name='admin/login.html', extra_context={'site_header': 'Medical Record System Login'}), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    
    # Application URLs
    path('', views.patient_list, name='patient_list'),
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/add/', views.add_patient, name='add_patient'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:pk>/book/', views.book_appointment, name='book_appointment'),
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/<int:pk>/schedule/', views.doctor_schedule, name='doctor_schedule'),
    path('doctors/<int:pk>/connect/', views.connect_doctor, name='connect_doctor'),
    # Appointments
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/<int:pk>/status/', views.update_appointment_status, name='update_appointment_status'),
    path('appointments/<int:pk>/edit/', views.edit_appointment, name='edit_appointment'),
    
    # Reports and Settings
    path('reports/', login_required(views.reports), name='reports'),
    path('settings/', login_required(views.settings_page), name='settings'),
]
