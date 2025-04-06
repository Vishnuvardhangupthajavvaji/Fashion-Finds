import unittest
import os
from flask import Flask
from app import create_app
import tempfile
import shutil

class TestGetImage(unittest.TestCase):
    def setUp(self):
        # Create test application
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        # Create temporary media directory
        self.temp_dir = tempfile.mkdtemp()
        self.app.config['UPLOAD_FOLDER'] = self.temp_dir
        
        self.client = self.app.test_client()
        
        # Verify the route exists
        self.app.view_functions['views.get_image']  # Will raise if route doesn't exist

    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir)

    def test_get_nonexistent_image_returns_404(self):
        """Test that missing images return 404"""
        response = self.client.get('/media/nonexistent.jpg')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data.decode(), "File not found")

    def test_image_path_security(self):
        """Test that path traversal attempts are blocked"""
        response = self.client.get('/media/../../../etc/passwd')
        self.assertEqual(response.status_code, 404)

    def test_route_exists(self):
        """Test that the image route is properly registered"""
        with self.app.test_request_context():
            # Verify the route exists in the url_map
            rules = [rule for rule in self.app.url_map.iter_rules() 
                    if rule.endpoint == 'views.get_image']
            self.assertTrue(len(rules) > 0, "Image route not registered")

if __name__ == '__main__':
    unittest.main()
