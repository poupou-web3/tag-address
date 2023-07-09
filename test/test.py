import unittest

from fastapi.testclient import TestClient
from src.main import app, ArrayInput


class TestMainApp(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_query_data(self):
        input_data = [1, 2, 3]  # replace this with your test data
        response = self.client.post(
            "/query",
            json={"data": input_data}  # replace this with your test data
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("result", response.json())
        self.assertEqual(input_data, response.json()['result'])
        # Add more assertions here based on your script's expected output


if __name__ == "__main__":
    unittest.main()
