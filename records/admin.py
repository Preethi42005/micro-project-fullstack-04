from django.contrib import admin
from .models import Patient, Doctor, Appointment, MedicalRecord

from .models import Vaccination, Medication, Billing, Message, DoctorAvailability

admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(Appointment)
admin.site.register(MedicalRecord)
admin.site.register(Vaccination)
admin.site.register(Medication)
admin.site.register(Billing)
admin.site.register(Message)
admin.site.register(DoctorAvailability)
