import unittest

# Import the function you want to test
from recommendation import get_recommendations  # Replace 'your_module' with the actual module name

class TestGetRecommendations(unittest.TestCase):

    def test_get_recommendations(self):
        # Define a sample cosine similarity matrix (replace with your actual data)
        cosine_sim = [[0.8, 0.6, 0.4], [0.6, 1.0, 0.2], [0.4, 0.2, 0.9]]

        # Define a sample DataFrame (replace with your actual data)
        df = {
            'id': [1, 2, 3],
            'name': ['Game 1', 'Game 2', 'Game 3'],
            'popularity': [80, 90, 70],
            'release_dates': ['2022-01-01', '2020-05-15', '2021-11-30']
        }

        # Mock the 'calculate_release_date_score' function
        def mock_calculate_release_date_score(date):
            return 0.9  # Replace with the expected release date score

        # Mock the 'open' function to capture JSON writing (replace with your actual JSON handling)
        class MockFile:
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc_val, exc_tb):
                pass
            def write(self, data):
                self.data = data

        def mock_open(filename, mode):
            return MockFile()

        # Replace 'your_module' with the actual module name
        with unittest.mock.patch('recommendation.calculate_release_date_score', side_effect=mock_calculate_release_date_score):
            with unittest.mock.patch('builtins.open', mock_open):
                result = get_recommendations(1, cosine_sim, df, num_recommend=2)

        # Replace the expected_output with the actual expected output
        expected_output = {
            '1': [
                {
                    'composite_score': 0.86,
                    'score': 0.75,
                    'popularity_score': 0.8,
                    'release_date_score': 0.9,
                    'id': 2,
                    'name': 'Game 2',
                    'released_date': '2020-05-15'
                },
                # Add more expected recommendations here if needed
            ]
        }

        self.assertEqual(result, expected_output)

if __name__ == '__main__':
    unittest.main()
