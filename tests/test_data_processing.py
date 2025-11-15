import pytest
import pandas as pd
import numpy as np

# It's good practice to have a separate module for data processing.
# For this example, I'll include a simplified version of the data cleaning functions
# from swapi_scraping.py. In a refactored project, these would be imported.

def clean_people_df(df):
    df.mass = df.mass.replace('unknown', np.nan)
    df.mass = df.mass.str.replace(',', '', regex=False)
    df.mass = df.mass.astype('float')
    df.height = df.height.replace('unknown', np.nan).astype('float')
    df.hair_color = df.hair_color.replace('n/a', np.nan)
    df.birth_year = df.birth_year.str.replace('BBY', ' BBY')
    return df

@pytest.fixture
def sample_people_df():
    """Provides a sample DataFrame for testing people data cleaning."""
    data = {
        'name': ['Luke Skywalker', 'C-3PO', 'Leia Organa'],
        'height': ['172', '167', '150'],
        'mass': ['77', '75', '49'],
        'hair_color': ['blond', 'n/a', 'brown'],
        'skin_color': ['fair', 'gold', 'light'],
        'eye_color': ['blue', 'yellow', 'brown'],
        'birth_year': ['19BBY', '112BBY', '19BBY'],
        'gender': ['male', 'n/a', 'female'],
    }
    return pd.DataFrame(data)

def test_clean_people_df_mass(sample_people_df):
    """Tests that the 'mass' column is cleaned correctly."""
    cleaned_df = clean_people_df(sample_people_df.copy())
    assert cleaned_df['mass'].dtype == 'float64'
    assert pd.isna(cleaned_df.loc[cleaned_df['name'] == 'C-3PO', 'mass'].iloc[0]) is False # In the original script it was not being converted to NaN
    assert cleaned_df.loc[cleaned_df['name'] == 'Luke Skywalker', 'mass'].iloc[0] == 77.0

def test_clean_people_df_height(sample_people_df):
    """Tests that the 'height' column is cleaned correctly."""
    cleaned_df = clean_people_df(sample_people_df.copy())
    assert cleaned_df['height'].dtype == 'float64'

def test_clean_people_df_hair_color(sample_people_df):
    """Tests that the 'hair_color' column is cleaned correctly."""
    cleaned_df = clean_people_df(sample_people_df.copy())
    assert pd.isna(cleaned_df.loc[cleaned_df['name'] == 'C-3PO', 'hair_color'].iloc[0])

def test_clean_people_df_birth_year(sample_people_df):
    """Tests that 'BBY' is correctly formatted in 'birth_year'."""
    cleaned_df = clean_people_df(sample_people_df.copy())
    assert cleaned_df.loc[cleaned_df['name'] == 'Luke Skywalker', 'birth_year'].iloc[0] == '19 BBY'

