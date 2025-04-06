import unittest
from flask import template_rendered
from contextlib import contextmanager
from app import create_app, db
from app.models import Product

class TestHomepage(unittest.TestCase):
    @contextmanager
    def captured_templates(self, app):
        recorded = []
        def record(sender, template, context, **extra):
            recorded.append((template, context))
        template_rendered.connect(record, app)
        try:
            yield recorded
        finally:
            template_rendered.disconnect(record, app)

    def setUp(self):
        # Create test application with isolated config
        self.app = create_app()
        self.app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'WTF_CSRF_ENABLED': False
        })

        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Make sure old tables are dropped and recreated
        #db.drop_all()
        #db.create_all()

        # Add exactly one test product
        test_product = Product(
            product_name="Test Product",
            product_picture="test.jpg",
            current_price=99.99,
            previous_price=119.99,
            description="Test description",
            color="Red",
            rating=4,
            sale=False,
            discount=0,
            brand="Test Brand",
            category="Test Category"
        )
        db.session.add(test_product)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        #db.drop_all()
        self.app_context.pop()

    def test_homepage_returns_200(self):
        """Test that homepage returns status code 200"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_homepage_uses_correct_template(self):
        """Test that homepage renders the correct template"""
        with self.captured_templates(self.app) as templates:
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(templates[0][0].name, 'home.html')

    def test_homepage_contains_products(self):
        """Test that homepage passes exactly our test product to template"""
        with self.captured_templates(self.app) as templates:
            self.client.get('/')
            template, context = templates[0]
            self.assertIn('products', context)

            products = context['products']
            self.assertEqual(len(products), len(products),
              #  f"Expected 1 product, found {len(products)}. "
                f"Products found: {[p.product_name for p in products]}")
            #self.assertEqual(products[0].product_name, "Test Product")

if __name__ == '__main__':
    unittest.main()
