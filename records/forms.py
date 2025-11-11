from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Appointment, MedicalRecord, Patient, Doctor, Department

class DateInput(forms.DateInput):
    input_type = 'date'

class TimeInput(forms.TimeInput):
    input_type = 'time'

class AppointmentForm(ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.now().date()
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        initial=datetime.strptime('09:00', '%H:%M').time()
    )
    
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time', 'notes', 'status', 'duration_minutes']
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': '15', 'step': '15'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['date'].initial = self.instance.date.date()
            self.fields['time'].initial = self.instance.date.time()
    
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        doctor = cleaned_data.get('doctor')
        duration = cleaned_data.get('duration_minutes', 30)
        
        if not all([date, time, doctor]):
            return cleaned_data
            
        # Combine date and time into a single datetime
        appointment_start = timezone.make_aware(
            datetime.combine(date, time)
        )
        appointment_end = appointment_start + timedelta(minutes=duration)
        
        # Check if appointment is in the past
        if appointment_start < timezone.now() - timedelta(hours=1):
            raise ValidationError("Appointment time cannot be in the past.")
        
        # Check for overlapping appointments with the same doctor
        overlapping = Appointment.objects.filter(
            doctor=doctor,
            date__lt=appointment_end,
            date__gte=appointment_start - timedelta(minutes=30),  # Assuming minimum 30 min buffer
            status__in=['scheduled', 'confirmed']
        ).exclude(pk=self.instance.pk if self.instance else None)
        
        if overlapping.exists():
            raise ValidationError("Doctor already has an appointment at this time.")
        
        # Set the combined datetime to the model's date field
        cleaned_data['date'] = appointment_start
        return cleaned_data

class MedicalRecordForm(ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['diagnosis', 'treatment', 'report']
        widgets = {
            'diagnosis': forms.TextInput(attrs={'class': 'form-control'}),
            'treatment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'report': forms.FileInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'report': 'Upload any medical reports or documents (optional)'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].initial = timezone.now().date()

class PatientForm(ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'dob', 'gender', 'phone', 'email', 'address', 'photo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'dob': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'placeholder': 'YYYY-MM-DD'
                }
            ),
            'gender': forms.Select(
                choices=[
                    ('', 'Select Gender'),
                    ('male', 'Male'),
                    ('female', 'Female'),
                    ('other', 'Other'),
                    ('prefer_not_to_say', 'Prefer not to say')
                ],
                attrs={'class': 'form-select'}
            ),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'photo': 'Upload a profile photo (optional)',
            'email': 'A valid email address (optional)'
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone and not phone.isdigit():
            raise ValidationError("Phone number should contain only digits.")
        return phone or None  # Allow empty phone numbers since it's optional
