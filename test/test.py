import unittest
import os
from pathlib import Path
import sys

import pandas as pd
import numpy as np

from fastapi.testclient import TestClient
from main import app
from main import run_model

app_path = os.path.join(Path.cwd().parent)
sys.path.append(app_path)

RESOURCE_FOLDER = "resources"

EXPECTED_RESULT_FEATURE1 = np.array([0, 0, 0, 1])


class TestMainApp(unittest.TestCase):
    path_to_test_data = os.path.join(Path.cwd(), RESOURCE_FOLDER, "features1.csv")
    df_features = pd.read_csv(path_to_test_data)
    df_features.set_index('eoa', inplace=True)

    os.chdir(app_path)

    def setUp(self):
        self.client = TestClient(app)

    def test_model(self):
        prediction = run_model(self.df_features, 'optimism')
        np.testing.assert_array_equal(prediction, EXPECTED_RESULT_FEATURE1)

    def test_query_data(self):
        input_data = self.df_features.index.tolist()
        response = self.client.post(
            "/infer/optimism",
            json={"address_list": input_data}  # replace this with your test data
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("result", response.json())
        prediction = pd.read_json(response.json()['result'], orient='split')
        np.testing.assert_array_equal(prediction['prediction'], EXPECTED_RESULT_FEATURE1)


if __name__ == "__main__":
    unittest.main()
