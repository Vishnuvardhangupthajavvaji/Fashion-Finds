import unittest
import warnings
from flask import template_rendered
from contextlib import contextmanager
from app import create_app, db
from app.models import Product, ProductSize
from sqlalchemy.exc import SAWarning

class TestProductDetails(unittest.TestCase):
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
        # Suppress SQLAlchemy deprecation warnings
        warnings.simplefilter("ignore", category=SAWarning)

        self.app = create_app()
        self.app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
            SQLALCHEMY_TRACK_MODIFICATIONS=False
        )
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        # Create a product
        product = Product(
            product_name="T-shirt",
            product_picture="kids.jpg",
            current_price=499.99,
            previous_price=599.99,
            description="comfortable t-shirt",
            color="Black",
            rating=4,
            sale=True,
            discount=20,
            brand="H&M",
            category="Kids"
        )
        db.session.add(product)
        db.session.commit()

        # Sizes
        sizes = [
            ProductSize(product_id=product.id, size='S', quantity=5),
            ProductSize(product_id=product.id, size='M', quantity=10),
            ProductSize(product_id=product.id, size='L', quantity=8),
        ]
        db.session.add_all(sizes)
        db.session.commit()

        self.product_id = product.id

    def tearDown(self):
        db.session.remove()
        #db.drop_all()
        self.app_context.pop()
        warnings.resetwarnings()  # Restore warnings to default after test

    def test_product_info_200(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = self.client.get(f'/product/{self.product_id}')
            self.assertEqual(response.status_code, 200)

    def test_product_info_invalid_id_404(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = self.client.get('/product/9999')
            self.assertEqual(response.status_code, 404)

    def test_product_info_template_context(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with self.captured_templates(self.app) as templates:
                response = self.client.get(f'/product/{self.product_id}')
                self.assertEqual(response.status_code, 200)
                template, context = templates[0]
                self.assertEqual(template.name, "product_details.html")
                self.assertEqual(context['product'].id, self.product_id)
                self.assertEqual(len(context['sizes']), 3)
                self.assertIn('suggested_products', context)

if __name__ == '__main__':
    unittest.main(warnings='ignore')
