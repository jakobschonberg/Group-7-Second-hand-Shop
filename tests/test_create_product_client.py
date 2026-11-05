import io
import os
import sqlite3
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import requests
from fastapi.testclient import TestClient

with patch("external_api.get_products_from_FakeStoreApi", return_value=[]), \
     patch("external_api.get_categories_from_FakeStoreApi", return_value=[]):
    import client
    from main import app
from seed import reset_database


class CreateProductClientTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = Path(self.folder.name) / "test.db"
        reset_database(self.path)
        self.env = patch.dict(os.environ, {
            "DATABASE_PATH": str(self.path),
            "API_KEY": "test-key",
            "REST_API_URL": "127.0.0.1:8000",
        })
        self.env.start()
        self.api = TestClient(app)
        self.headers = {"X-API-Key": "test-key"}

    def tearDown(self):
        self.api.close()
        self.env.stop()
        self.folder.cleanup()

    def request(self, method, url, **kwargs):
        self.assertTrue(url.startswith("http://127.0.0.1:8000/"))
        self.assertEqual(kwargs.pop("timeout"), 10)
        result = self.api.request(method, url, **kwargs)
        response = requests.Response()
        response.status_code = result.status_code
        response._content = result.content
        return response

    def run_menu_action(self, name="Desk lamp", category="Electronics",
                        price="25", stock="2"):
        output = io.StringIO()
        with patch("builtins.input", side_effect=[name, category, price, stock]), \
             patch("client.requests.post", side_effect=lambda url, **kw: self.request("POST", url, **kw)), \
             redirect_stdout(output):
            client.create_product_via_api()
        return output.getvalue()

    def query(self, sql):
        conn = sqlite3.connect(self.path)
        try:
            return conn.execute(sql).fetchall()
        finally:
            conn.close()

    def test_existing_category_and_saved_product(self):
        categories_before = self.query('SELECT count(*) FROM categories')
        self.assertIn("successfully", self.run_menu_action(category="electronics"))
        self.assertEqual(self.query("SELECT category_id, price, stock FROM products WHERE name='Desk lamp'"), [(2, 25.0, 2)])
        self.assertEqual(self.query("SELECT count(*) FROM categories"), categories_before)

    def test_new_category_and_duplicate_product(self):
        self.assertIn("successfully", self.run_menu_action(category="Furniture"))
        self.assertEqual(self.query("SELECT count(*) FROM categories WHERE name='Furniture'"), [(1,)])
        self.assertIn("already exists", self.run_menu_action(category="Furniture"))
        self.assertEqual(self.query("SELECT count(*) FROM products WHERE name='Desk lamp'"), [(1,)])

    def test_invalid_inputs_do_not_send_requests(self):
        for price, stock in [("-1", "2"), ("nan", "2"), ("abc", "2"), ("2", "1.5")]:
            with patch("client.requests.post") as post, patch("builtins.input", side_effect=["Lamp", "Tools", price, stock]), redirect_stdout(io.StringIO()):
                client.create_product_via_api()
                post.assert_not_called()

    def test_category_auth_and_validation(self):
        for headers in [{}, {"X-API-Key": "wrong"}]:
            result = self.api.post("/categories", headers=headers, json={"name": "Tools"})
            self.assertEqual(result.status_code, 401)
        result = self.api.post("/categories", headers=self.headers, json={"name": " "})
        self.assertEqual(result.status_code, 422)

    def test_connection_failure_and_missing_key(self):
        with patch("builtins.input", side_effect=["Lamp", "Tools", "2", "3"]), \
             patch("client.requests.post", side_effect=requests.ConnectionError), \
             redirect_stdout(io.StringIO()) as output:
            client.create_product_via_api()
        self.assertIn("Could not contact", output.getvalue())
        with patch.dict(os.environ, {"API_KEY": ""}), redirect_stdout(io.StringIO()) as output:
            client.create_product_via_api()
        self.assertIn("Set API_KEY", output.getvalue())

    def test_http_and_malformed_responses(self):
        for status, content, message in [
            (401, b'{}', 'API request failed (401)'),
            (500, b'{}', 'API request failed (500)'),
            (200, b'not json', 'unexpected response'),
        ]:
            response = requests.Response()
            response.status_code = status
            response._content = content
            with patch("builtins.input", side_effect=["Lamp", "Tools", "2", "3"]), \
                 patch("client.requests.post", return_value=response), \
                 redirect_stdout(io.StringIO()) as output:
                client.create_product_via_api()
            self.assertIn(message, output.getvalue())


if __name__ == "__main__":
    unittest.main()
