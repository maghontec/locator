import pandas as pd
import numpy as np

def load_and_clean_data(file_path):
    """Load and clean the hospitals dataset."""
    df = pd.read_csv(file_path)

    # Convert GPS coordinates to float
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

    # Remove invalid coordinates
    df = df[
        (df['latitude'].notna()) & 
        (df['longitude'].notna()) &
        (df['latitude'] != 0) & 
        (df['longitude'] != 0)
    ]

    # Clean boolean columns
    bool_columns = [
        'maternal_health_delivery_services',
        'emergency_transport',
        'skilled_birth_attendant',
        'phcn_electricity',
        'c_section_yn',
        'improved_water_supply',
        'improved_sanitation',
        'vaccines_fridge_freezer',
        'antenatal_care_yn',
        'family_planning_yn',
        'malaria_treatment_artemisinin'
    ]

    for col in bool_columns:
        df[col] = df[col].map({'TRUE': True, 'FALSE': False})

    return df

def get_facility_stats(df):
    """Calculate basic statistics about healthcare facilities."""
    stats = {
        'total_facilities': len(df),
        'facility_types': df['facility_type_display'].value_counts().to_dict(),
        'states': 36,  # Fixed number of states in Nigeria
        'lgas': df['Local_Government_Area'].nunique(),
        'with_electricity': df['phcn_electricity'].sum(),
        'with_water': df['improved_water_supply'].sum(),
        'with_emergency': df['emergency_transport'].sum()
    }
    return stats

def get_location_options(df):
    """Get unique states and their corresponding LGAs."""
    # Get unique states
    states = sorted(df['State'].unique())

    # Create a dictionary of state to LGAs
    state_to_lgas = {
        state: sorted(df[df['State'] == state]['Local_Government_Area'].unique())
        for state in states
    }

    return states, state_to_lgas

def filter_facilities(df, facility_type=None, services=None, search_term=None, state=None, lga=None):
    """Filter facilities based on type, services, search term, state, and LGA."""
    filtered_df = df.copy()

    if facility_type and facility_type != "All":
        filtered_df = filtered_df[filtered_df['facility_type_display'] == facility_type]

    if services:
        for service in services:
            if service == "Maternal Health":
                filtered_df = filtered_df[filtered_df['maternal_health_delivery_services'] == True]
            elif service == "Emergency Transport":
                filtered_df = filtered_df[filtered_df['emergency_transport'] == True]
            elif service == "Family Planning":
                filtered_df = filtered_df[filtered_df['family_planning_yn'] == True]
            elif service == "Malaria Treatment":
                filtered_df = filtered_df[filtered_df['malaria_treatment_artemisinin'] == True]

    if state:
        filtered_df = filtered_df[filtered_df['State'] == state]

    if lga:
        filtered_df = filtered_df[filtered_df['Local_Government_Area'] == lga]

    if search_term:
        search_mask = (
            filtered_df['facility_name'].str.contains(search_term, case=False, na=False) |
            filtered_df['State'].str.contains(search_term, case=False, na=False) |
            filtered_df['Local_Government_Area'].str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[search_mask]

    return filtered_df