import unittest
from flask import template_rendered
from contextlib import contextmanager
from app import create_app, db
from app.models import Product

class TestSearchFunctionality(unittest.TestCase):

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
        self.app = create_app()
        self.app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
        })
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        # Insert test products
        products = [
            Product(
                product_name="Red T-Shirt",
                product_picture="red.jpg",
                current_price=25.00,
                previous_price=30.00,
                description="A red comfy shirt",
                color="red",
                category="Men",
                rating=4
            ),
            Product(
                product_name="Blue Jeans",
                product_picture="jeans.jpg",
                current_price=50.00,
                previous_price=60.00,
                description="Classic denim",
                color="blue",
                category="Women",
                rating=5
            ),
            Product(
            product_name='Red Dress',
            product_picture='reddress.jpg',
            current_price=49.99,
            previous_price=59.99,
            description='Elegant red dress for women',
            color='red',
            category='Women',
            rating=5,
            sale=True,
            discount=10
        ),


            Product(
                product_name="Green Dress",
                product_picture="dress.jpg",
                current_price=45.00,
                previous_price=55.00,
                description="Elegant evening dress",
                color="green",
                category="Kids",
                rating=5
            )
        ]
        db.session.bulk_save_objects(products)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        #db.drop_all()
        self.app_context.pop()

    def test_search_by_query(self):
        with self.captured_templates(self.app) as templates:
            response = self.client.get('/search?query=shirt')
            self.assertEqual(response.status_code, 200)
            template, context = templates[0]
            product_names = [p.product_name for p in context['products']]
            self.assertIn("Red T-Shirt", product_names)

    '''def test_search_by_color(self):
        with self.captured_templates(self.app) as templates:
            response = self.client.get('/search?color=blue')
            self.assertEqual(response.status_code, 200)
            template, context = templates[0]
            self.assertTrue(all(p.color == 'blue' for p in context['products']))

    def test_search_by_category(self):
        with self.captured_templates(self.app) as templates:
            response = self.client.get('/search?category=Women')
            self.assertEqual(response.status_code, 200)
            template, context = templates[0]
            self.assertEqual(len(context['products']), 2)'''

    def test_search_by_price_range(self):
        with self.captured_templates(self.app) as templates:
            response = self.client.get('/search?min_price=40&max_price=50')
            self.assertEqual(response.status_code, 200)
            template, context = templates[0]
            prices = [p.current_price for p in context['products']]
            self.assertTrue(all(40 <= price <= 50 for price in prices))

if __name__ == '__main__':
    unittest.main()


