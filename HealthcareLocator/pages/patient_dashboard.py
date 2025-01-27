import streamlit as st
import datetime
from database import get_db
from models import MedicalHistory, Allergy, HealthVisit
from sqlalchemy.orm import Session

# Custom CSS for Nigerian theme
st.markdown("""
    <style>
    .patient-header {
        color: #008751;
        font-size: 2.5em;
        font-weight: bold;
        text-align: center;
        padding: 1em 0;
        border-bottom: 2px solid #008751;
        margin-bottom: 1em;
    }
    .section-card {
        background-color: #ffffff;
        padding: 1.5em;
        border-radius: 10px;
        border: 2px solid #008751;
        margin-bottom: 1em;
    }
    .info-text {
        color: #666;
        font-size: 0.9em;
    }
    .success-text {
        color: #008751;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

def get_patient_data(db: Session, email: str):
    """Fetch all patient-related data"""
    from models import Patient
    patient = db.query(Patient).filter(Patient.email == email).first()
    if not patient:
        return None
    return patient

def update_medical_history(db: Session, patient_id: int, medical_conditions: str, 
                         surgical_history: str, family_history: str, current_medications: str):
    """Update patient's medical history"""
    history = db.query(MedicalHistory).filter(MedicalHistory.patient_id == patient_id).first()
    if not history:
        history = MedicalHistory(
            patient_id=patient_id,
            medical_conditions=medical_conditions,
            surgical_history=surgical_history,
            family_history=family_history,
            current_medications=current_medications
        )
        db.add(history)
    else:
        history.medical_conditions = medical_conditions
        history.surgical_history = surgical_history
        history.family_history = family_history
        history.current_medications = current_medications
        history.last_updated = datetime.datetime.utcnow()
    
    db.commit()
    return history

def add_allergy(db: Session, patient_id: int, allergen: str, reaction: str, severity: str):
    """Add a new allergy record"""
    allergy = Allergy(
        patient_id=patient_id,
        allergen=allergen,
        reaction=reaction,
        severity=severity,
        diagnosed_date=datetime.datetime.utcnow()
    )
    db.add(allergy)
    db.commit()
    return allergy

def add_visit(db: Session, patient_id: int, facility_id: str, reason: str, notes: str, follow_up_needed: bool):
    """Add a new health visit record"""
    visit = HealthVisit(
        patient_id=patient_id,
        facility_id=facility_id,
        visit_date=datetime.datetime.utcnow(),
        reason=reason,
        notes=notes,
        follow_up_needed=follow_up_needed
    )
    db.add(visit)
    db.commit()
    return visit

def patient_dashboard():
    st.title("Patient Dashboard")

    # Check authentication
    if not st.session_state.get("authentication_status"):
        st.warning("Please log in to access your dashboard")
        st.switch_page("pages/patient_auth.py")
        return

    try:
        db = next(get_db())
        patient = get_patient_data(db, st.session_state["patient_email"])
        
        if not patient:
            st.error("Patient data not found")
            return

        # Display patient info
        st.header(f"Welcome, {patient.full_name}")
        
        # Create tabs for different sections
        medical_tab, allergies_tab, visits_tab = st.tabs([
            "Medical History", "Allergies", "Health Visits"
        ])

        with medical_tab:
            st.subheader("Medical History")
            
            # Get existing medical history
            history = patient.medical_history

            # Create form for medical history
            with st.form("medical_history_form"):
                medical_conditions = st.text_area(
                    "Medical Conditions",
                    value=history.medical_conditions if history else "",
                    height=100
                )
                surgical_history = st.text_area(
                    "Surgical History",
                    value=history.surgical_history if history else "",
                    height=100
                )
                family_history = st.text_area(
                    "Family History",
                    value=history.family_history if history else "",
                    height=100
                )
                current_medications = st.text_area(
                    "Current Medications",
                    value=history.current_medications if history else "",
                    height=100
                )
                
                if st.form_submit_button("Update Medical History"):
                    updated_history = update_medical_history(
                        db, patient.id, medical_conditions, surgical_history,
                        family_history, current_medications
                    )
                    st.success("Medical history updated successfully!")

        with allergies_tab:
            st.subheader("Allergies")
            
            # Display existing allergies
            if patient.allergies:
                st.write("Current Allergies:")
                for allergy in patient.allergies:
                    with st.expander(f"{allergy.allergen} - {allergy.severity}"):
                        st.write(f"Reaction: {allergy.reaction}")
                        st.write(f"Diagnosed: {allergy.diagnosed_date.strftime('%Y-%m-%d')}")
            
            # Form to add new allergy
            with st.form("add_allergy_form"):
                st.write("Add New Allergy")
                allergen = st.text_input("Allergen")
                reaction = st.text_area("Reaction")
                severity = st.selectbox("Severity", ["Mild", "Moderate", "Severe"])
                
                if st.form_submit_button("Add Allergy"):
                    if allergen and reaction:
                        new_allergy = add_allergy(db, patient.id, allergen, reaction, severity)
                        st.success("Allergy added successfully!")
                        st.rerun()
                    else:
                        st.error("Please fill in all required fields")

        with visits_tab:
            st.subheader("Health Visits")
            
            # Display existing visits
            if patient.visits:
                st.write("Visit History:")
                for visit in sorted(patient.visits, key=lambda x: x.visit_date, reverse=True):
                    with st.expander(f"Visit on {visit.visit_date.strftime('%Y-%m-%d')}"):
                        st.write(f"Reason: {visit.reason}")
                        st.write(f"Notes: {visit.notes}")
                        st.write(f"Follow-up needed: {'Yes' if visit.follow_up_needed else 'No'}")
            
            # Form to add new visit
            with st.form("add_visit_form"):
                st.write("Add New Visit")
                facility_id = st.text_input("Facility ID")
                reason = st.text_area("Reason for Visit")
                notes = st.text_area("Visit Notes")
                follow_up = st.checkbox("Follow-up Needed")
                
                if st.form_submit_button("Add Visit"):
                    if facility_id and reason and notes:
                        new_visit = add_visit(
                            db, patient.id, facility_id, reason, notes, follow_up
                        )
                        st.success("Visit record added successfully!")
                        st.rerun()
                    else:
                        st.error("Please fill in all required fields")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    patient_dashboard()