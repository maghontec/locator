from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    date_of_birth = Column(DateTime)
    phone_number = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    medical_history = relationship("MedicalHistory", back_populates="patient", uselist=False)
    allergies = relationship("Allergy", back_populates="patient")
    visits = relationship("HealthVisit", back_populates="patient")

class MedicalHistory(Base):
    __tablename__ = "medical_histories"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    medical_conditions = Column(Text)
    surgical_history = Column(Text)
    family_history = Column(Text)
    current_medications = Column(Text)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    patient = relationship("Patient", back_populates="medical_history")

class Allergy(Base):
    __tablename__ = "allergies"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    allergen = Column(String)
    reaction = Column(String)
    severity = Column(String)  # mild, moderate, severe
    diagnosed_date = Column(DateTime)
    
    # Relationship
    patient = relationship("Patient", back_populates="allergies")

class HealthVisit(Base):
    __tablename__ = "health_visits"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    facility_id = Column(String)  # References the facility from Hospitals.csv
    visit_date = Column(DateTime)
    reason = Column(Text)
    notes = Column(Text)
    follow_up_needed = Column(Boolean, default=False)
    
    # Relationship
    patient = relationship("Patient", back_populates="visits")
