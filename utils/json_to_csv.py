import csv
import json

# Load the JSON data
with open('../assets/all_recommendations055.json', 'r') as json_file:
    data = json.load(json_file)

# Open a CSV file for writing
with open('../assets/all_recommendations055.csv', 'w', newline='') as csv_file:
    fieldnames = ['game_id', 'recommended_game_id', 'composite_score']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    # Iterate through the JSON data and flatten it
    for game_id, recommendations in data.items():
        for recommendation in recommendations:
            writer.writerow({
                'game_id': game_id,
                'recommended_game_id': recommendation['id'],
                'composite_score': recommendation['composite_score']
            })
