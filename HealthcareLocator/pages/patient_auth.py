import streamlit as st
import datetime
from database import get_db
from auth import create_patient, authenticate_patient, create_access_token
from datetime import timedelta

def patient_auth_page():
    st.title("Patient Portal")

    # Initialize session state variables if they don't exist
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = None

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.header("Login")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Login")

            if submit_login:
                try:
                    db = next(get_db())
                    patient = authenticate_patient(db, email, password)
                    if patient:
                        access_token = create_access_token(
                            data={"sub": patient.email},
                            expires_delta=timedelta(minutes=30)
                        )
                        st.session_state["patient_token"] = access_token
                        st.session_state["patient_email"] = patient.email
                        st.session_state["authentication_status"] = True
                        st.success("Login successful! Redirecting to dashboard...")
                        st.rerun()
                    else:
                        st.error("Invalid email or password")
                except Exception as e:
                    st.error(f"Login failed: {str(e)}")

    with tab2:
        st.header("Register")
        with st.form("register_form"):
            new_email = st.text_input("Email")
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            full_name = st.text_input("Full Name")

            # Date of birth input using three number inputs
            st.write("Date of Birth:")
            col1, col2, col3 = st.columns(3)
            with col1:
                year = st.number_input("Year", min_value=1900, max_value=datetime.datetime.now().year, value=2000)
            with col2:
                month = st.number_input("Month", min_value=1, max_value=12, value=1)
            with col3:
                day = st.number_input("Day", min_value=1, max_value=31, value=1)

            phone_number = st.text_input("Phone Number")
            submit_register = st.form_submit_button("Register")

            if submit_register:
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    try:
                        # Create date object from the inputs
                        date_of_birth = datetime.date(year, month, day)

                        db = next(get_db())
                        patient = create_patient(
                            db=db,
                            email=new_email,
                            username=new_username,
                            password=new_password,
                            full_name=full_name,
                            date_of_birth=datetime.datetime.combine(date_of_birth, datetime.time()),
                            phone_number=phone_number
                        )
                        st.success("Registration successful! Please login.")
                    except ValueError as e:
                        st.error(f"Invalid date: {str(e)}")
                    except Exception as e:
                        st.error(f"Registration failed: {str(e)}")

    # Check authentication status and redirect if logged in
    if st.session_state.get("authentication_status"):
        st.switch_page("pages/patient_dashboard.py")

if __name__ == "__main__":
    patient_auth_page()