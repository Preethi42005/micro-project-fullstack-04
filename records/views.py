from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from .models import Patient, Doctor, Appointment, Billing, MedicalRecord, Vaccination, Medication
from .forms import AppointmentForm, MedicalRecordForm, PatientForm
from .services import sms_service

def patient_list(request):
    patients = Patient.objects.all()
    return render(request, 'records/patient_list.html', {'patients': patients})

from .models import Doctor, Appointment

def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(request, 'records/doctor_list.html', {'doctors': doctors})

def appointment_list(request):
    try:
        # Get all appointments with related patient and doctor data
        appointments = Appointment.objects.select_related('patient', 'doctor').order_by('-date').all()
        
        # Add pagination
        paginator = Paginator(appointments, 10)  # Show 10 appointments per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Get page range for pagination
        index = page_obj.number - 1
        max_index = len(paginator.page_range)
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index
        page_range = list(paginator.page_range)[start_index:end_index]
        
        return render(request, 'records/appointment_list.html', {
            'appointments': page_obj,
            'page_range': page_range,
        })
        
    except Exception as e:
        print(f"Error in appointment_list: {str(e)}")
        return render(request, 'records/appointment_list.html', {
            'appointments': [],
            'error': 'Failed to load appointments. Please try again later.'
        })

# Add patient view
from django.shortcuts import redirect
from .models import Patient
from django import forms

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'dob', 'address']

def add_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('patient_list')
    else:
        form = PatientForm()
    return render(request, 'records/add_patient.html', {'form': form})


from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.contrib import messages
from .models import MedicalRecord, Vaccination, Medication, Billing, Appointment, TimeSlot
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from .models import DoctorAvailability, Doctor, Message, Patient
from django.views.decorators.http import require_http_methods
import logging


class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['diagnosis', 'treatment', 'report']


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'notes']

    def clean(self):
        cleaned = super().clean()
        doctor = cleaned.get('doctor')
        date = cleaned.get('date')
        if not doctor or not date:
            return cleaned
        duration = getattr(self.instance, 'duration_minutes', 30)
        new_start = date
        new_end = date + timedelta(minutes=duration)
        # check overlapping appointments for the doctor
        overlapping = Appointment.objects.filter(doctor=doctor, status='scheduled').exclude(pk=self.instance.pk)
        for appt in overlapping:
            appt_start = appt.date
            appt_end = appt.date + timedelta(minutes=appt.duration_minutes)
            if appt_start < new_end and appt_end > new_start:
                raise forms.ValidationError('This time overlaps with another appointment for the selected doctor.')
        return cleaned


def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    records = MedicalRecord.objects.filter(patient=patient).order_by('-date_recorded')
    vaccinations = Vaccination.objects.filter(patient=patient).order_by('-date_given')
    medications = Medication.objects.filter(patient=patient)
    bills = Billing.objects.filter(patient=patient).order_by('-created_at')

    # handle medical record upload
    if request.method == 'POST' and 'add_record' in request.POST:
        form = MedicalRecordForm(request.POST, request.FILES)
        if form.is_valid():
            rec = form.save(commit=False)
            rec.patient = patient
            rec.save()
            return redirect('appointment_list')
    else:
        form = MedicalRecordForm()

    return render(request, 'records/patient_detail.html', {
        'patient': patient,
        'records': records,
        'vaccinations': vaccinations,
        'medications': medications,
        'bills': bills,
        'form': form,
    })


def book_appointment(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            try:
                appt = form.save(commit=False)
                appt.patient = patient
                appt.save()
                
                # For AJAX requests, return success with redirect URL
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'redirect_url': reverse('appointment_list')
                    })
                return redirect('appointment_list')
                
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': str(e)
                    }, status=400)
                messages.error(request, f'An error occurred: {str(e)}')
        
        # Handle form errors for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data()
            }, status=400)
            
        messages.error(request, 'Please correct the errors below.')
    else:
        form = AppointmentForm()
    return render(request, 'records/book_appointment.html', {'form': form, 'patient': patient})


def doctor_schedule(request, pk):
    try:
        doctor = get_object_or_404(Doctor, pk=pk)
        
        # Get available time slots for the next 7 days
        today = timezone.now().date()
        end_date = today + timedelta(days=7)
        
        # Get available time slots, excluding those that are already booked
        time_slots = TimeSlot.objects.filter(
            doctor=doctor,
            start__date__range=[today, end_date],
            available=True,
            start__gt=timezone.now()  # Only show future time slots
        ).order_by('start')
        
        context = {
            'doctor': doctor,
            'time_slots': time_slots,
            'today': today,
            'end_date': end_date
        }
        
        return render(request, 'records/doctor_schedule.html', context)
        
    except Exception as e:
        messages.error(request, f"An error occurred while loading the schedule: {str(e)}")
        return redirect('doctor_list')


@require_http_methods(["GET", "POST"])
def connect_doctor(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    patient = getattr(request.user, 'patient', None)
    
    if request.method == 'POST':
        # Handle message sending
        content = request.POST.get('content', '').strip()
        if content and patient:
            message = Message.objects.create(
                sender_patient=patient,
                sender_doctor=None,
                content=content,
                doctor=doctor
            )
            
            return redirect('connect_doctor', pk=pk)
        return redirect('doctor_list')
    
    # If user is not authenticated, redirect to login with a message
    if not request.user.is_authenticated:
        from django.contrib import messages
        messages.warning(
            request,
            'Please log in to connect with a doctor. Your message will be saved after login.'
        )
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(
            next=request.path,
            login_url='/admin/login/'
        )
    
    return render(request, 'records/connect_doctor.html', {
        'doctor': doctor,
        'form': {
            'message': request.GET.get('message', '')
        }
    })


from django.http import HttpResponse, JsonResponse
import pandas as pd
from io import BytesIO
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required

@login_required
def reports(request):
    """View for displaying and exporting reports."""
    export_format = request.GET.get('export')
    
    # Get appointment statistics
    total_appointments = Appointment.objects.count()
    completed_appointments = Appointment.objects.filter(status='completed').count()
    pending_appointments = Appointment.objects.filter(status='pending').count()
    cancelled_appointments = Appointment.objects.filter(status='cancelled').count()
    
    # Prepare appointment summary data
    appointments_summary = {
        'total': total_appointments,
        'completed': completed_appointments,
        'pending': pending_appointments,
        'cancelled': cancelled_appointments
    }
    
    # Sample data - replace with your actual data
    reports_data = [
        {'patient': 'John Doe', 'appointment_date': '2025-11-15', 'status': 'Scheduled'},
        {'patient': 'Jane Smith', 'appointment_date': '2025-11-16', 'status': 'Completed'},
        # Add more sample data or fetch from your models
    ]
    
    if export_format in ['csv', 'excel']:
        df = pd.DataFrame(reports_data)
        
        if export_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=reports.csv'
            df.to_csv(response, index=False)
            return response
            
        elif export_format == 'excel':
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Reports')
            
            response = HttpResponse(
                output.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename=reports.xlsx'
            return response
    
    context = {
        'title': 'Reports',
        'reports': reports_data,
        'appointments_summary': appointments_summary,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'pending_appointments': pending_appointments,
        'cancelled_appointments': cancelled_appointments
    }
    
    return render(request, 'records/reports.html', context)


def settings_page(request):
    # Add settings view logic here
    return render(request, 'records/settings.html', {'title': 'Settings'})

@require_http_methods(["POST"])
@csrf_exempt  # For simplicity, in production use proper CSRF handling
@login_required
def update_appointment_status(request, pk):
    try:
        data = json.loads(request.body)
        appointment = Appointment.objects.get(pk=pk)
        new_status = data.get('status')
        
        if new_status in dict(Appointment.STATUS_CHOICES).keys():
            appointment.status = new_status
            appointment.save()
            return JsonResponse({'success': True, 'message': 'Appointment status updated successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid status'}, status=400)
    except Appointment.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Appointment not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
def edit_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appointment updated successfully.')
            return redirect('appointment_list')
    else:
        form = AppointmentForm(instance=appointment)
    
    return render(request, 'records/book_appointment.html', {
        'form': form,
        'title': 'Edit Appointment',
        'patient': appointment.patient,
        'is_edit': True
    })
