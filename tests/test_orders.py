import os
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from fastapi.testclient import TestClient

# Supplier data is unrelated to these tests; avoid network calls at import.
with patch('external_api.get_products_from_FakeStoreApi', return_value=[]), \
     patch('external_api.get_categories_from_FakeStoreApi', return_value=[]):
    from main import app
    import database
from seed import reset_database


class OrderTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = Path(self.folder.name) / 'test.db'
        reset_database(self.path)
        self.env = patch.dict(os.environ, {
            'DATABASE_PATH': str(self.path), 'API_KEY': 'test-key'
        })
        self.env.start()
        self.client = TestClient(app)
        self.headers = {'X-API-Key': 'test-key'}

    def tearDown(self):
        self.client.close()
        self.env.stop()
        self.folder.cleanup()

    def query(self, sql):
        with closing(sqlite3.connect(self.path)) as conn:
            return conn.execute(sql).fetchall()

    def post(self, items, customer_id=1):
        return self.client.post('/orders', headers=self.headers, json={
            'customer_id': customer_id, 'items': items
        })

    def test_single_order_and_saved_price(self):
        response = self.post([{'product_id': 1, 'quantity': 2}])
        self.assertEqual(response.status_code, 201)
        order = response.json()
        self.assertEqual(order['status'], 'NEW')
        self.assertEqual(order['items'][0]['unit_price'], 50)
        self.assertEqual(self.query('SELECT stock FROM products WHERE product_id=1'), [(8,)])
        with closing(sqlite3.connect(self.path)) as conn:
            conn.execute('UPDATE products SET price=99 WHERE product_id=1')
            conn.commit()
        saved = self.client.get(f"/orders/{order['order_id']}").json()
        self.assertEqual(saved['items'][0]['unit_price'], 50)
        filtered = self.client.get('/orders?customer_id=1').json()
        self.assertTrue(all(row['customer_id'] == 1 for row in filtered))
        self.assertEqual(len(self.client.get('/orders').json()), 5)

    def test_multiple_products_and_repeated_product(self):
        response = self.post([
            {'product_id': 1, 'quantity': 2},
            {'product_id': 3, 'quantity': 1},
            {'product_id': 1, 'quantity': 3},
        ])
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.json()['items']), 2)
        self.assertEqual(self.query('SELECT stock FROM products WHERE product_id IN (1,3) ORDER BY product_id'), [(5,), (0,)])

    def test_failure_rolls_back_everything(self):
        for second_id, quantity, status in [(2, 1, 409), (999, 1, 404), (1, 10, 409)]:
            with self.subTest(second_id=second_id):
                response = self.post([
                    {'product_id': 1, 'quantity': 1},
                    {'product_id': second_id, 'quantity': quantity},
                ])
                self.assertEqual(response.status_code, status)
                self.assertEqual(self.query('SELECT count(*) FROM orders'), [(4,)])
                self.assertEqual(self.query('SELECT count(*) FROM order_items'), [(5,)])
                self.assertEqual(self.query('SELECT stock FROM products WHERE product_id=1'), [(10,)])

    def test_missing_resources(self):
        self.assertEqual(self.post([{'product_id': 1, 'quantity': 1}], 999).status_code, 404)
        self.assertEqual(self.client.get('/orders/999').status_code, 404)
        self.assertEqual(self.client.get('/orders?customer_id=999').json(), [])
        self.assertEqual(self.client.patch('/orders/999', headers=self.headers, json={'status': 'DELIVERED'}).status_code, 404)

    def test_validation(self):
        for quantity in [0, -1, 1.5, True, '2']:
            self.assertEqual(self.post([{'product_id': 1, 'quantity': quantity}]).status_code, 422)
        self.assertEqual(self.post([]).status_code, 422)
        self.assertEqual(self.client.patch('/orders/1', headers=self.headers, json={'status': 'NEW', 'customer_id': 2}).status_code, 422)
        self.assertEqual(self.client.patch('/orders/1', headers=self.headers, json={'status': 'PAID'}).status_code, 422)
        self.assertEqual(self.client.get('/orders?customer_id=0').status_code, 422)

    def test_api_key(self):
        for headers in [{}, {'X-API-Key': 'wrong'}]:
            self.assertEqual(self.client.post('/orders', headers=headers, json={'customer_id': 1, 'items': [{'product_id': 1, 'quantity': 1}]}).status_code, 401)
            self.assertEqual(self.client.patch('/orders/1', headers=headers, json={'status': 'CANCELLED'}).status_code, 401)
        with patch.dict(os.environ, {'API_KEY': ''}):
            self.assertEqual(self.post([{'product_id': 1, 'quantity': 1}]).status_code, 401)

    def test_cancel_restores_stock_once(self):
        order = self.post([{'product_id': 1, 'quantity': 3}]).json()
        url = f"/orders/{order['order_id']}"
        for _ in range(2):
            response = self.client.patch(url, headers=self.headers, json={'status': 'CANCELLED'})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(self.query('SELECT stock FROM products WHERE product_id=1'), [(10,)])
        self.assertEqual(self.client.patch(url, headers=self.headers, json={'status': 'NEW'}).status_code, 409)

    def test_delivered_keeps_stock(self):
        order = self.post([{'product_id': 3, 'quantity': 1}]).json()
        url = f"/orders/{order['order_id']}"
        self.assertEqual(self.client.patch(url, headers=self.headers, json={'status': 'DELIVERED'}).status_code, 200)
        self.assertEqual(self.query('SELECT stock FROM products WHERE product_id=3'), [(0,)])
        self.assertEqual(self.client.patch(url, headers=self.headers, json={'status': 'CANCELLED'}).status_code, 409)

    def test_two_orders_cannot_buy_last_item(self):
        def buy():
            try:
                database.create_order({'customer_id': 1, 'items': [{'product_id': 3, 'quantity': 1}]})
                return 'created'
            except ValueError:
                return 'no stock'
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: buy(), range(2)))
        self.assertCountEqual(results, ['created', 'no stock'])
        self.assertEqual(self.query('SELECT stock FROM products WHERE product_id=3'), [(0,)])
        self.assertEqual(self.query('PRAGMA foreign_key_check'), [])


if __name__ == '__main__':
    unittest.main()
