import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from utils import load_and_clean_data, get_facility_stats, filter_facilities, get_location_options
from database import init_db
import requests
from folium import plugins

# Initialize database
init_db()

# Page config
st.set_page_config(
    page_title="Nigerian Healthcare Facilities Explorer",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-family: 'sans serif';
        font-size: 3em;
        font-weight: bold;
        color: #008751;  /* Nigerian green */
        text-align: center;
        padding: 1em 0;
        border-bottom: 2px solid #008751;
        margin-bottom: 1em;
    }
    .sub-header {
        color: #008751;
        font-size: 1.5em;
        font-weight: bold;
        margin: 1em 0;
    }
    .stat-card {
        background-color: #ffffff;
        padding: 1em;
        border-radius: 10px;
        border: 2px solid #008751;
        text-align: center;
    }
    .stat-card h3 {
        color: #008751;
        margin-bottom: 0.5em;
    }
    </style>
""", unsafe_allow_html=True)

# Add login/register button in the sidebar
if not st.session_state.get("authentication_status"):
    if st.sidebar.button("Login/Register"):
        st.switch_page("pages/patient_auth.py")
else:
    # Show logout button in sidebar
    if st.sidebar.button("Logout"):
        st.session_state["authentication_status"] = None
        st.session_state["patient_token"] = None
        st.session_state["patient_email"] = None
        st.rerun()

    st.sidebar.write(f"Logged in as: {st.session_state.get('patient_email', 'Unknown')}")

# Load and clean data
@st.cache_data
def load_data():
    return load_and_clean_data("attached_assets/Hospitals.csv")

try:
    df = load_data()
    states, state_to_lgas = get_location_options(df)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Main header with Nigerian theme
st.markdown('<h1 class="main-header">🇳🇬 Nigerian Healthcare Facilities Explorer</h1>', unsafe_allow_html=True)

# Introduction text
st.markdown("""
    <div style='padding: 1em; background-color: #f0f2f6; border-radius: 10px; margin-bottom: 2em;'>
        Welcome to the Nigerian Healthcare Facilities Explorer. This platform provides comprehensive information 
        about healthcare facilities across Nigeria, helping you locate and learn about medical services in your area.
        Get directions to any facility by clicking on the markers and selecting your preferred mode of transport.
    </div>
""", unsafe_allow_html=True)

# Sidebar filters with improved styling
st.sidebar.markdown('<h2 style="color: #008751;">Search Filters</h2>', unsafe_allow_html=True)

# Location filters
selected_state = st.sidebar.selectbox("Select State", ["All"] + states)
selected_lga = None
if selected_state != "All":
    lga_options = state_to_lgas.get(selected_state, [])
    selected_lga = st.sidebar.selectbox(
        "Select LGA",
        ["All"] + lga_options
    )

# Facility type filter
facility_types = ["All"] + sorted(df['facility_type_display'].unique().tolist())
selected_type = st.sidebar.selectbox("Facility Type", facility_types)

# Services filter
available_services = [
    "Maternal Health",
    "Emergency Transport",
    "Family Planning",
    "Malaria Treatment"
]
selected_services = st.sidebar.multiselect("Available Services", available_services)

# Search box
search_term = st.sidebar.text_input("🔍 Search by name or location")

# Filter data
state_filter = selected_state if selected_state != "All" else None
lga_filter = selected_lga if selected_lga and selected_lga != "All" else None

filtered_df = filter_facilities(
    df,
    facility_type=selected_type,
    services=selected_services,
    search_term=search_term,
    state=state_filter,
    lga=lga_filter
)

# Statistics cards with Nigerian theme
st.markdown('<h2 class="sub-header">Healthcare Overview</h2>', unsafe_allow_html=True)
stats = get_facility_stats(df)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
        <div class="stat-card">
            <h3>Total Facilities</h3>
            <h2>{:,}</h2>
        </div>
    """.format(stats['total_facilities']), unsafe_allow_html=True)
with col2:
    st.markdown("""
        <div class="stat-card">
            <h3>States Covered</h3>
            <h2>{:,}</h2>
        </div>
    """.format(stats['states']), unsafe_allow_html=True)
with col3:
    st.markdown("""
        <div class="stat-card">
            <h3>LGAs Covered</h3>
            <h2>{:,}</h2>
        </div>
    """.format(stats['lgas']), unsafe_allow_html=True)

# Map section
st.markdown('<h2 class="sub-header">Interactive Facilities Map</h2>', unsafe_allow_html=True)

# Add transportation mode selection
transport_mode = st.radio(
    "Select transportation mode for directions:",
    ["🚗 Driving", "🚲 Cycling", "🚶 Walking"],
    horizontal=True
)

try:
    # Initialize the map
    m = folium.Map(
        location=[9.0820, 8.6753],  # Nigeria's center
        zoom_start=6,
        width=800,
        height=600
    )

    # Add location control
    plugins.LocateControl().add_to(m)

    # Add routing control
    plugins.Geocoder().add_to(m)

    # Add markers with Nigerian colors
    for idx, row in filtered_df.iterrows():
        if idx > 1000:
            break

        # Define marker color based on facility type with Nigerian theme
        colors = {
            'Teaching / Specialist Hospital': '#008751',  # Nigerian green
            'District / General Hospital': '#0000FF',     # Blue
            'Primary Health Centre (PHC)': '#008751',     # Nigerian green
            'Health Post': '#FFA500',                     # Orange
            'Dispensary': '#800080'                       # Purple
        }
        color = colors.get(row['facility_type_display'], 'gray')

        # Enhanced popup content with directions button
        popup_html = f"""
        <div style='width: 250px; padding: 10px; font-family: Arial;'>
            <h4 style='color: #008751; margin-bottom: 10px;'>{row['facility_name']}</h4>
            <b style='color: #666;'>Type:</b> {row['facility_type_display']}<br>
            <b style='color: #666;'>State:</b> {row['State']}<br>
            <b style='color: #666;'>LGA:</b> {row['Local_Government_Area']}<br>
            <div style='margin-top: 10px;'>
                <b style='color: #008751;'>Services:</b><br>
                {'✓' if row['maternal_health_delivery_services'] else '✗'} Maternal Health<br>
                {'✓' if row['emergency_transport'] else '✗'} Emergency Transport<br>
                {'✓' if row['family_planning_yn'] else '✗'} Family Planning<br>
                {'✓' if row['malaria_treatment_artemisinin'] else '✗'} Malaria Treatment
            </div>
            <div style='margin-top: 10px; text-align: center;'>
                <a href='https://www.google.com/maps/dir/?api=1&destination={row['latitude']},{row['longitude']}'
                   target='_blank' style='
                   background-color: #008751;
                   color: white;
                   padding: 8px 15px;
                   border-radius: 5px;
                   text-decoration: none;
                   display: inline-block;
                   margin-top: 10px;
                   '>
                    Get Directions 🗺️
                </a>
            </div>
        </div>
        """

        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=6,
            popup=folium.Popup(popup_html, max_width=300),
            color=color,
            fill=True
        ).add_to(m)

    # Display map
    map_data = st_folium(m, width=800)

except Exception as e:
    st.error(f"Error rendering map: {e}")

# Footer with Nigerian theme
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Data source: Nigerian Healthcare Facilities Database</p>
        <p style='margin: 10px 0;'><strong>Contact Us:</strong> <a href="mailto:admin@nhcservice.com" style='color: #008751;'>admin@nhcservice.com</a></p>
        <p style='color: #008751;'>🇳🇬 Supporting Healthcare Access Across Nigeria 🇳🇬</p>
    </div>
""", unsafe_allow_html=True)