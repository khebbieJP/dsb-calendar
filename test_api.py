#!/usr/bin/env python3
"""
Automated tests for Flask API endpoints
"""

import pytest
from pathlib import Path
from app import app


class TestFlaskAPI:
    """Test suite for Flask web API"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    @pytest.fixture
    def test_pdf_path(self):
        """Return the path to the test PDF"""
        return Path("Billet.pdf")

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')

        assert response.status_code == 200
        assert response.is_json

        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'DSB Ticket to ICS Converter'
        assert data['version'] == '1.0.0'

    def test_homepage(self, client):
        """Test homepage loads"""
        response = client.get('/')

        assert response.status_code == 200
        assert b'DSB Ticket to Calendar' in response.data

    def test_convert_to_json(self, client, test_pdf_path):
        """Test PDF conversion to JSON format"""
        if not test_pdf_path.exists():
            pytest.skip(f"{test_pdf_path} not found")

        with open(test_pdf_path, 'rb') as f:
            response = client.post('/api/convert', data={
                'file': (f, 'Billet.pdf'),
                'format': 'json'
            }, content_type='multipart/form-data')

        assert response.status_code == 200
        assert response.is_json

        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'formatted' in data

        # Verify extracted data
        ticket_data = data['data']
        assert ticket_data['from_station'] == 'Aarhus H'
        assert ticket_data['to_station'] == 'København H'
        assert ticket_data['train_type'] == 'InterCityLyn'
        assert ticket_data['train_number'] == '42'

        # Verify formatted data
        formatted = data['formatted']
        assert formatted['from'] == 'Aarhus H'
        assert formatted['to'] == 'København H'
        assert '2025-11-14 13:15' in formatted['departure']

    def test_convert_to_ics(self, client, test_pdf_path):
        """Test PDF conversion to ICS format"""
        if not test_pdf_path.exists():
            pytest.skip(f"{test_pdf_path} not found")

        with open(test_pdf_path, 'rb') as f:
            response = client.post('/api/convert', data={
                'file': (f, 'Billet.pdf'),
                'format': 'ics'
            }, content_type='multipart/form-data')

        assert response.status_code == 200
        assert response.mimetype == 'text/calendar'

        # Verify ICS content
        ics_data = response.data.decode('utf-8')
        assert 'BEGIN:VCALENDAR' in ics_data
        assert 'BEGIN:VEVENT' in ics_data
        assert 'DSB Rejse' in ics_data
        assert 'Aarhus H' in ics_data
        assert 'København H' in ics_data
        assert 'END:VEVENT' in ics_data
        assert 'END:VCALENDAR' in ics_data

    def test_no_file_uploaded(self, client):
        """Test error when no file is uploaded"""
        response = client.post('/api/convert', data={},
                              content_type='multipart/form-data')

        assert response.status_code == 400
        assert response.is_json

        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'No file provided'

    def test_invalid_file_type(self, client):
        """Test error when non-PDF file is uploaded"""
        from io import BytesIO

        response = client.post('/api/convert', data={
            'file': (BytesIO(b'not a pdf'), 'test.txt'),
        }, content_type='multipart/form-data')

        assert response.status_code == 400
        assert response.is_json

        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'Invalid file type'

    def test_404_handler(self, client):
        """Test 404 error handler"""
        response = client.get('/nonexistent')

        assert response.status_code == 404
        assert response.is_json

        data = response.get_json()
        assert data['error'] == 'Not found'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
