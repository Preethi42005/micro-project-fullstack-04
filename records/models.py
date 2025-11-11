from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    dob = models.DateField()
    address = models.TextField()
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    last_visit = models.DateField(null=True, blank=True)
    # optional profile photo
    photo = models.ImageField(upload_to='patient_photos/', null=True, blank=True)

    def __str__(self):
        return self.name


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    experience_years = models.PositiveIntegerField(default=0)
    bio = models.TextField(blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateTimeField()
    notes = models.TextField(blank=True)
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    # duration of appointment in minutes
    duration_minutes = models.PositiveIntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    # duration in minutes (used to detect overlapping appointments)
    duration_minutes = models.PositiveIntegerField(default=30)


class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    diagnosis = models.CharField(max_length=255)
    treatment = models.TextField()
    date_recorded = models.DateTimeField(auto_now_add=True)
    # allow storing a report file
    report = models.FileField(upload_to='medical_reports/', null=True, blank=True)


class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date_prescribed = models.DateTimeField(auto_now_add=True)
    medication = models.CharField(max_length=255)
    dosage = models.CharField(max_length=255)
    instructions = models.TextField()
    prescription_file = models.FileField(upload_to='prescriptions/', null=True, blank=True)

    def __str__(self):
        return f"Prescription for {self.patient} by {self.doctor} on {self.date_prescribed}"


class TreatmentPlan(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return f"Treatment plan for {self.patient}"


class Vaccination(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    vaccine_name = models.CharField(max_length=200)
    date_given = models.DateField()
    notes = models.TextField(blank=True)


class DoctorAvailability(models.Model):
    """Weekly recurring availability for a doctor.

    day_of_week: 0=Monday .. 6=Sunday
    """
    DAY_CHOICES = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'),
        (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ]
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availabilities')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ['doctor', 'day_of_week', 'start_time']

    def __str__(self):
        return f"{self.doctor.name} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class Medication(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    dosage_instructions = models.TextField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)


class Billing(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)


class Message(models.Model):
    # simple patient-doctor messaging
    sender_patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True)
    sender_doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class TimeSlot(models.Model):
    """Represents an available time slot for a doctor. Used to seed available bookings or for admin editing."""
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    start = models.DateTimeField()
    end = models.DateTimeField()
    available = models.BooleanField(default=True)

    class Meta:
        ordering = ['doctor', 'start']

    def __str__(self):
        return f"{self.doctor.name}: {self.start} - {self.end} ({'available' if self.available else 'busy'})"
