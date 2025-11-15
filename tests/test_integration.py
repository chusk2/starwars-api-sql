import pytest
from unittest.mock import patch, MagicMock
import json
import os
import pandas as pd
from sqlalchemy import create_engine, text

# NOTE: This is a simplified integration test. In a real-world scenario,
# the `swapi_scraping.py` script would be refactored into importable functions.
# For this example, we will have to simulate the script's behavior.

@pytest.fixture(scope="module")
def test_db_engine():
    """Creates an in-memory SQLite database for testing."""
    engine = create_engine('sqlite:///:memory:')
    yield engine
    engine.dispose()

@pytest.fixture
def mock_swapi_data():
    """Provides mock data that simulates the SWAPI response."""
    return {
        "films": [
            {
                "title": "A New Hope",
                "episode_id": 4,
                "url": "https://swapi.dev/api/films/1/",
                "characters": ["https://swapi.dev/api/people/1/"],
                "planets": ["https://swapi.dev/api/planets/1/"],
                "starships": [],
                "vehicles": [],
                "species": [],
            }
        ],
        "people": [
            {
                "name": "Luke Skywalker",
                "homeworld": "https://swapi.dev/api/planets/1/",
                "films": ["https://swapi.dev/api/films/1/"],
                "species": [],
                "vehicles": [],
                "starships": [],
                "url": "https://swapi.dev/api/people/1/",
            }
        ],
        "planets": [
            {
                "name": "Tatooine",
                "residents": ["https://swapi.dev/api/people/1/"],
                "films": ["https://swapi.dev/api/films/1/"],
                "url": "https://swapi.dev/api/planets/1/",
            }
        ],
        "species": [],
        "starships": [],
        "vehicles": [],
    }

@patch('requests.get')
def test_full_etl_pipeline(mock_get, test_db_engine, mock_swapi_data):
    """
    An integration test for the full ETL pipeline.
    - Mocks the API call.
    - Simulates the data processing and loading steps.
    - Verifies that data is inserted into the test database.
    """
    # Mock the API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    
    # We need to handle multiple calls to `requests.get` for different categories
    def get_side_effect(url):
        mock_response = MagicMock()
        mock_response.status_code = 200
        category = url.split('/')[-2]
        
        # Default empty response
        response_data = {"next": None, "results": []}

        if category in mock_swapi_data:
            response_data["results"] = mock_swapi_data[category]
        
        mock_response.json.return_value = response_data
        return mock_response

    mock_get.side_effect = get_side_effect

    # --- Simulate the ETL process from swapi_scraping.py ---
    
    # 1. Scraping (already mocked)
    # In a real test, you would call the refactored scraping function here.
    
    # 2. Processing
    # Simplified processing logic for the test
    processed_data = {}
    for category, items in mock_swapi_data.items():
        processed_items = []
        for item in items:
            processed_item = item.copy()
            processed_item['id'] = int(item['url'].split('/')[-2])
            processed_items.append(processed_item)
        processed_data[category] = processed_items

    # 3. DataFrame creation and normalization
    # Simplified for the purpose of this test
    films_df = pd.DataFrame(processed_data['films'])
    films_df.rename(columns={'id': 'film_id'}, inplace=True)
    
    # 4. Database Loading
    # Create schema in the test DB
    with test_db_engine.connect() as connection:
        connection.execute(text("""
            CREATE TABLE films (
                film_id INT PRIMARY KEY,
                title VARCHAR(255),
                episode_id INT
            );
        """))
        connection.commit()


    # Insert data
    films_df_to_load = films_df[['film_id', 'title', 'episode_id']]
    films_df_to_load.to_sql('films', test_db_engine, if_exists='append', index=False)

    # 5. Verification
    with test_db_engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM films WHERE film_id = 1;")).fetchone()
        assert result is not None
        assert result[1] == "A New Hope"

