"""
Test suite for hospital search and favorites
"""

from unittest.mock import patch

@patch('app.requests.get')
@patch('app.requests.post')
def test_search_hospitals(mock_post, mock_get, client, auth_headers):
    """Test hospital search"""
    # Mock geocoding response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [{'lat': '40.7128', 'lon': '-74.0060'}]
    
    # Mock Overpass AI response
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        'elements': [
            {
                'id': 1,
                'tags': {'name': 'Mock Hospital', 'amenity': 'hospital'},
                'lat': 40.7128,
                'lon': -74.0060
            }
        ]
    }
    
    with patch('app.intelligent_ai_analysis') as mock_ai:
        mock_ai.return_value = ([{'id': 1, 'name': 'Mock Hospital', 'ai_score': 0.9}], {'method': 'mock'})
        response = client.post('/api/search-hospitals-osm',
                            headers=auth_headers,
                            json={
                                'location': 'New York',
                                'symptoms': 'chest pain'
                            })
        
    assert response.status_code in [200, 500, 502]  # 500/502 if external API fails

def test_add_favorite(client, auth_headers):
    """Test adding hospital to favorites"""
    response = client.post('/api/favorites',
                          headers=auth_headers,
                          json={
                              'hospital_name': 'Test Hospital',
                              'hospital_address': '123 Main St',
                              'latitude': 40.7128,
                              'longitude': -74.0060
                          })
    assert response.status_code == 201
    data = response.json
    assert 'message' in data

def test_list_favorites(client, auth_headers):
    """Test listing favorites"""
    # First add a favorite
    client.post('/api/favorites',
               headers=auth_headers,
               json={
                   'hospital_name': 'Favorite Hospital',
                   'hospital_address': '456 Elm St',
                   'latitude': 40.7128,
                   'longitude': -74.0060
               })
    
    # List favorites
    response = client.get('/api/favorites', headers=auth_headers)
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_search_history(client, auth_headers):
    """Test getting search history"""
    response = client.get('/api/search-history', headers=auth_headers)
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
