from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.utils import timezone
from datetime import datetime, timedelta
import random
import os
from faker import Faker

from records.models import (
    Department, Patient, Doctor, Appointment, MedicalRecord,
    Prescription, TreatmentPlan, Vaccination, DoctorAvailability,
    Medication, Billing, Message, TimeSlot
)

class Command(BaseCommand):
    help = 'Populates the database with sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to seed database...'))
        
        # Clear existing data
        self.clear_data()
        
        # Create data
        self.create_departments()
        self.create_users()
        self.create_patients()
        self.create_doctors()
        self.create_appointments()
        self.create_medical_records()
        self.create_prescriptions()
        self.create_treatment_plans()
        self.create_vaccinations()
        self.create_doctor_availabilities()
        self.create_medications()
        self.create_billings()
        self.create_messages()
        self.create_time_slots()
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))
    
    def clear_data(self):
        """Clear existing data from all models"""
        models = [
            TimeSlot, Message, Billing, Medication, DoctorAvailability,
            Vaccination, TreatmentPlan, Prescription, MedicalRecord,
            Appointment, Doctor, Patient, Department, Group, User
        ]
        
        for model in models:
            model.objects.all().delete()
    
    def create_departments(self):
        departments = [
            'Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 
            'Dermatology', 'General Medicine'
        ]
        
        for dept in departments:
            Department.objects.get_or_create(
                name=dept,
                description=f"{dept} Department"
            )
        self.stdout.write(self.style.SUCCESS(f'Created {len(departments)} departments'))
    
    def create_users(self):
        # Create admin user
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        
        # Create staff groups
        doctor_group = Group.objects.create(name='Doctors')
        staff_group = Group.objects.create(name='Staff')
        
        # Add permissions to groups
        doctor_perms = [
            'add_patient', 'change_patient', 'view_patient',
            'add_appointment', 'change_appointment', 'view_appointment',
            'add_medicalrecord', 'change_medicalrecord', 'view_medicalrecord',
            'add_prescription', 'view_prescription',
        ]
        
        for perm in doctor_perms:
            doctor_group.permissions.add(Permission.objects.get(codename=perm))
        
        self.stdout.write(self.style.SUCCESS('Created admin user and groups'))
    
    def create_patients(self):
        fake = Faker()
        
        for i in range(1, 6):  # Create 5 patients
            user = User.objects.create_user(
                username=f'patient{i}',
                email=f'patient{i}@example.com',
                password='patient123',
                first_name=fake.first_name(),
                last_name=fake.last_name()
            )
            
            patient = Patient.objects.create(
                user=user,
                name=f"{user.first_name} {user.last_name}",
                dob=fake.date_of_birth(minimum_age=18, maximum_age=90),
                address=fake.address(),
                email=user.email,
                phone=fake.phone_number(),
                gender=random.choice(['Male', 'Female', 'Other']),
                last_visit=fake.date_between(start_date='-1y', end_date='today')
            )
        
        self.stdout.write(self.style.SUCCESS('Created 5 patients'))
    
    def create_doctors(self):
        departments = list(Department.objects.all())
        specialties = [
            'Cardiologist', 'Neurologist', 'Orthopedic Surgeon', 
            'Pediatrician', 'Dermatologist', 'General Physician'
        ]
        
        for i in range(1, 6):  # Create 5 doctors
            first_name = Faker().first_name()
            last_name = Faker().last_name()
            email = f'dr.{first_name.lower()}.{last_name.lower()}@example.com'
            
            user = User.objects.create_user(
                username=f'dr.{first_name.lower()}.{last_name.lower()}',
                email=email,
                password='doctor123',
                first_name=f'Dr. {first_name}',
                last_name=last_name
            )
            
            doctor = Doctor.objects.create(
                user=user,
                name=f"Dr. {first_name} {last_name}",
                specialization=random.choice(specialties),
                experience_years=random.randint(2, 30),
                bio=Faker().paragraph(nb_sentences=3),
                department=random.choice(departments)
            )
            
            # Add to doctors group
            doctor_group = Group.objects.get(name='Doctors')
            user.groups.add(doctor_group)
        
        self.stdout.write(self.style.SUCCESS('Created 5 doctors'))
    
    def create_appointments(self):
        patients = list(Patient.objects.all())
        doctors = list(Doctor.objects.all())
        statuses = ['scheduled', 'completed', 'cancelled']
        
        # Create 1-2 appointments per patient
        for patient in patients:
            for _ in range(random.randint(1, 2)):
                doctor = random.choice(doctors)
                days_ago = random.randint(1, 30)
                days_ahead = random.randint(1, 14)
                
                # Randomly choose past or future date
                if random.choice([True, False]):
                    date = timezone.now() - timedelta(days=days_ago)
                    status = random.choice(['completed', 'cancelled'])
                else:
                    date = timezone.now() + timedelta(days=days_ahead)
                    status = 'scheduled'
                
                Appointment.objects.create(
                    patient=patient,
                    doctor=doctor,
                    date=date,
                    status=status,
                    notes=f"Appointment notes for {patient.name}"
                )
        
        self.stdout.write(self.style.SUCCESS(f'Created {Appointment.objects.count()} appointments'))
    
    def create_medical_records(self):
        patients = list(Patient.objects.all())
        
        # Create 1 medical record per patient
        for patient in patients:
            MedicalRecord.objects.create(
                patient=patient,
                diagnosis=f"Diagnosis for {patient.name}",
                treatment="Standard treatment plan including medication and follow-up",
                date_recorded=timezone.now() - timedelta(days=random.randint(1, 30))
            )
        
        self.stdout.write(self.style.SUCCESS('Created medical records for all patients'))
    
    def create_prescriptions(self):
        patients = list(Patient.objects.all())
        doctors = list(Doctor.objects.all())
        
        medications = [
            'Amoxicillin', 'Ibuprofen', 'Lisinopril', 
            'Metformin', 'Atorvastatin', 'Omeprazole'
        ]
        
        for patient in patients:
            # 1-2 prescriptions per patient
            for _ in range(random.randint(1, 2)):
                Prescription.objects.create(
                    patient=patient,
                    doctor=random.choice(doctors),
                    medication=random.choice(medications),
                    dosage=f"{random.randint(1, 3)} tablet(s) {random.choice(['once', 'twice', 'three times'])} a day",
                    instructions=Faker().sentence(),
                    date_prescribed=Faker().date_time_between(
                        start_date='-1y',
                        end_date='now'
                    )
                )
        
        self.stdout.write(self.style.SUCCESS('Created prescriptions for all patients'))
    
    def create_treatment_plans(self):
        patients = list(Patient.objects.all())
        doctors = list(Doctor.objects.all())
        
        # Create treatment plans for all patients (5 total)
        for patient in patients:
            start_date = Faker().date_between(start_date='-6m', end_date='+1m')
            TreatmentPlan.objects.create(
                patient=patient,
                doctor=random.choice(doctors),
                start_date=start_date,
                end_date=start_date + timedelta(days=random.randint(30, 90)),
                description=Faker().paragraph(nb_sentences=2)
            )
        
        self.stdout.write(self.style.SUCCESS('Created treatment plans for 5 patients'))
    
    def create_vaccinations(self):
        patients = list(Patient.objects.all())
        vaccines = [
            'Influenza', 'Tetanus', 'Hepatitis B', 
            'MMR', 'COVID-19', 'Flu'
        ]
        
        for patient in patients:
            # Each patient gets 1-2 random vaccinations
            for _ in range(random.randint(1, 2)):
                Vaccination.objects.create(
                    patient=patient,
                    vaccine_name=random.choice(vaccines),
                    date_given=Faker().date_between(start_date='-5y', end_date='today'),
                    notes=Faker().sentence()
                )
        
        self.stdout.write(self.style.SUCCESS('Created vaccination records for all patients'))
    
    def create_doctor_availabilities(self):
        doctors = list(Doctor.objects.all())
        days = [0, 1, 2, 3, 4]  # Monday to Friday
        
        for doctor in doctors:
            for day in random.sample(days, k=random.randint(3, 5)):  # 3-5 working days
                DoctorAvailability.objects.create(
                    doctor=doctor,
                    day_of_week=day,
                    start_time=timezone.datetime.strptime('09:00', '%H:%M').time(),
                    end_time=timezone.datetime.strptime('17:00', '%H:%M').time()
                )
        
        self.stdout.write(self.style.SUCCESS('Created doctor availabilities'))
    
    def create_medications(self):
        patients = list(Patient.objects.all())
        
        medications_list = [
            ('Lisinopril', '10mg once daily for blood pressure'),
            ('Metformin', '500mg twice daily with meals for diabetes'),
            ('Atorvastatin', '20mg at bedtime for cholesterol'),
            ('Levothyroxine', '50mcg every morning on empty stomach'),
            ('Albuterol', '2 puffs every 4-6 hours as needed for wheezing')
        ]
        
        for patient in patients:
            # Each patient gets 1-2 medications
            for _ in range(random.randint(1, 2)):
                med_name, dosage = random.choice(medications_list)
                Medication.objects.create(
                    patient=patient,
                    name=med_name,
                    dosage_instructions=dosage,
                    start_date=Faker().date_between(start_date='-1y', end_date='today'),
                    end_date=Faker().date_between(start_date='today', end_date='+1y') if random.choice([True, False]) else None
                )
        
        self.stdout.write(self.style.SUCCESS('Created medication records for all patients'))
    
    def create_billings(self):
        patients = list(Patient.objects.all())
        statuses = [True] * 8 + [False] * 2  # 80% paid, 20% unpaid
        
        for patient in patients:
            # Create 1 billing record per patient
            amount = random.randint(50, 500)
            Billing.objects.create(
                patient=patient,
                amount=amount,
                description=f"Consultation fee {Faker().month_name()} {timezone.now().year}",
                paid=random.choice(statuses)
            )
        
        self.stdout.write(self.style.SUCCESS('Created billing records for all patients'))
    
    def create_messages(self):
        patients = list(Patient.objects.all())
        doctors = list(Doctor.objects.all())
        
        for _ in range(50):  # Create 50 messages
            sender_patient = random.choice(patients)
            sender_doctor = random.choice(doctors)
            
            # Randomly decide if message is from patient to doctor or vice versa
            if random.choice([True, False]):
                Message.objects.create(
                    sender_patient=sender_patient,
                    content=Faker().paragraph(nb_sentences=2),
                    timestamp=Faker().date_time_between(start_date='-30d', end_date='now')
                )
            else:
                Message.objects.create(
                    sender_doctor=sender_doctor,
                    content=Faker().paragraph(nb_sentences=2),
                    timestamp=Faker().date_time_between(start_date='-30d', end_date='now')
                )
        
        self.stdout.write(self.style.SUCCESS('Created 50 messages'))
    
    def create_time_slots(self):
        doctors = list(Doctor.objects.all())
        today = timezone.now().date()
        
        for doctor in doctors:
            # Create time slots for the next 7 days
            for day in range(7):
                date = today + timedelta(days=day)
                # Skip weekends
                if date.weekday() >= 5:  # 5=Saturday, 6=Sunday
                    continue
                    
                # Create 4 time slots per day (9am-1pm)
                for hour in range(9, 13):
                    start_time = timezone.datetime.combine(
                        date, 
                        timezone.datetime.min.time().replace(hour=hour)
                    )
                    end_time = start_time + timedelta(hours=1)
                    
                    TimeSlot.objects.create(
                        doctor=doctor,
                        start=start_time,
                        end=end_time,
                        available=random.choice([True, True, True, False])  # 75% chance of being available
                    )
        
        self.stdout.write(self.style.SUCCESS('Created time slots for doctors'))
