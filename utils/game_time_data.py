import json
from howlongtobeatpy import HowLongToBeat
from concurrent.futures import ThreadPoolExecutor, as_completed


class GameTimeMatcher:
    def __init__(self, hltb):
        self.hltb = hltb
        self.cache = {}

    def _get_game_time(self, game_data):
        game_name = game_data['name']

        # Check if the game information is available in the cache
        if game_name in self.cache:
            result = self.cache[game_name]
        else:
            results = self.hltb.search(game_name)
            result = results[0] if results else None

            # Update the cache with the game information
            self.cache[game_name] = result

        return game_data, result

    def map_time_to_beat(self, filename):
        # Load game data from JSON file
        with open(filename) as f:
            games_data = json.load(f)

        # Variables to store matched games and unmatched games
        matched_games = []
        unmatched_games = []

        # Retrieve information for each game using parallel processing
        with ThreadPoolExecutor() as executor:
            # Create a list of futures
            futures = [executor.submit(self._get_game_time, game_data) for game_data in games_data]

            # Wait for all futures to complete and process the results
            for future in as_completed(futures):
                game_data, result = future.result()
                if result:
                    game_data['main_story'] = result.main_story
                    game_data['main_extra'] = result.main_extra
                    game_data['completionist'] = result.completionist
                    matched_games.append(game_data)
                    print(f"Game matched: {game_data['name']}")
                else:
                    unmatched_games.append(game_data)

        # Export matched game data to the same JSON file
        with open(filename, 'w') as f:
            json.dump(matched_games, f, indent=4)

        print(f"Total games matched: {len(matched_games)}")
        print(f"Total games not matched: {len(unmatched_games)}")


# Usage example
hltb = HowLongToBeat()
filename = '../assets/games.json'

matcher = GameTimeMatcher(hltb)
matcher.map_time_to_beat(filename)
