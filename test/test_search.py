import unittest
from app import app  # Import your Flask app
import json


class TestSearchEndpoint(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_search_by_title(self):
        # Define a valid query
        valid_query = "spiderman"

        # Prepare a request with the valid query
        response = self.app.post('/game/search', data=json.dumps({'query': valid_query}),
                                 content_type='application/json')

        # Check the response status code
        self.assertEqual(response.status_code, 200)

        # Parse the response data as a JSON object
        response_data = json.loads(response.data)

        # Check the response content based on your expectations
        self.assertEqual(response_data['query'], "spiderman")
        self.assertEqual(response_data['corrected_query'], "spiderman")

        # Check the content of the first result
        first_result = response_data['content'][0]
        self.assertEqual(first_result['id'], 2050)
        self.assertEqual(first_result['cover'], "//images.igdb.com/igdb/image/upload/t_cover_big/co5bze.jpg")
        self.assertEqual(first_result['genres'], [
            "Puzzle",
            "Hack and slash/Beat 'em up",
            "Adventure"
        ])
        self.assertEqual(first_result['name'], "lego marvel super heroes")
        self.assertEqual(first_result['summary'],
                         "in lego marvel super heroes players will unlock more than 100 characters from across the "
                         "marvel universe including fan favorites like spiderman iron man wolverine captain america "
                         "the hulk thor black widow hawkeye deadpool loki and galactus the game will pack in a "
                         "plethora of supercool character abilities combatlike action sequences epic battle scenes "
                         "puzzlesolving and a unique story told with playful lego humor")
        self.assertEqual(first_result['url'], "https://www.igdb.com/games/lego-marvel-super-heroes")
        self.assertEqual(first_result['websites'], [
            [
                "http://www.lego.com/marvelsuperheroes",
                "Official"
            ],
            [
                "https://store.steampowered.com/app/249130",
                "Steam"
            ],
            [
                "https://en.wikipedia.org/wiki/Lego_Marvel_Super_Heroes",
                "Wikipedia"
            ],
            [
                "https://itunes.apple.com/us/app/lego-marvel-super-heroes/id737006024?mt=8&uo=4",
                "iPhone"
            ],
            [
                "https://play.google.com/store/apps/details?id=com.wb.lego.marvel&hl=en&gl=us",
                "Android"
            ],
            [
                "https://brickipedia.fandom.com/wiki/LEGO_Marvel_Super_Heroes",
                "Wikia"
            ],
            [
                "https://www.twitch.tv/directory/game/LEGO%20Marvel%20Super%20Heroes",
                "Twitch"
            ]
        ])
        self.assertEqual(first_result['main_story'], 12.28)
        self.assertEqual(first_result['main_extra'], 23.71)
        self.assertEqual(first_result['completionist'], 40.2)
        self.assertEqual(first_result['aggregated_rating'], 84.6316)
        self.assertEqual(first_result['aggregated_rating_count'], 20)
        self.assertEqual(first_result['rating'], 79.2609)
        self.assertEqual(first_result['rating_count'], 162)
        self.assertEqual(first_result['release_dates'], "2013-09-30")
        self.assertEqual(first_result['storyline'],
                         "lego marvel super heroes offers an original storyline in which nick fury calls upon iron "
                         "man the hulk thor spiderman wolverine and other heroes spanning the marvel universe to save "
                         "earth from such threats as the vengeance of loki and the hunger of galactus devourer of the "
                         "worlds lego and marvel fans will enjoy classic lego videogame adventure and humor while "
                         "playing as their favorite marvel characters")
        self.assertEqual(first_result['unclean_name'], "LEGO Marvel Super Heroes")
        self.assertEqual(first_result['unclean_summary'],
                         "In LEGO Marvel Super Heroes, players will unlock more than 100 characters from across the "
                         "Marvel Universe, including fan favorites like Spider-Man, Iron Man, Wolverine, "
                         "Captain America, the Hulk, Thor, Black Widow, Hawkeye, Deadpool, Loki and Galactus! The "
                         "game will pack in a plethora of super-cool character abilities, combat-like action "
                         "sequences, epic battle scenes, puzzle-solving and a unique story told with playful LEGO "
                         "humor.")
        self.assertEqual(first_result['popularity'], 0.692116)

    def test_search_by_description(self):
        # Define a valid query
        valid_query = "the Guardians discover an artifact of unspeakable power"

        # Prepare a request with the valid query
        response = self.app.post('/game/search', data=json.dumps({'query': valid_query}),
                                 content_type='application/json')

        # Check the response status code
        self.assertEqual(response.status_code, 200)

        # Parse the response data as a JSON object
        response_data = json.loads(response.data)

        # Check the response content based on your expectations
        self.assertEqual(response_data['query'], "the Guardians discover an artifact of unspeakable power")
        self.assertEqual(response_data['corrected_query'], "the Guardians discover an artifact of unspeakable power")

        # Check the content of the first result
        first_result = response_data['content'][0]
        self.assertEqual(first_result['id'], 26165)
        self.assertEqual(first_result['cover'], "//images.igdb.com/igdb/image/upload/t_cover_big/co27yt.jpg")
        self.assertEqual(first_result['genres'], [
            "Point-and-click",
            "Role-playing (RPG)",
            "Adventure"
        ])
        self.assertEqual(first_result['name'], "marvels guardians of the galaxy the telltale series")
        self.assertEqual(first_result['summary'],
                         "marvels guardians of the galaxy the telltale series is a brand new story of the universes "
                         "unlikeliest heroes starlord gamora drax rocket and groot in the wake of an epic battle the "
                         "guardians discover an artifact of unspeakable power each of them has a reason to desire "
                         "this relic as does a ruthless enemy who is the last of her kind and who will stop at "
                         "nothing to tear it from their hands\n\nfrom earth to the milano to knowhere and beyond and "
                         "set to the beat of awesome music you wear the rocketpowered boots of starlord in an "
                         "original guardians adventure where your decisions and actions drive the story you "
                         "experience")
        self.assertEqual(first_result['url'],
                         "https://www.igdb.com/games/marvels-guardians-of-the-galaxy-the-telltale-series")
        self.assertEqual(first_result['websites'], [
            [
                "https://www.facebook.com/telltalegames",
                "Facebook"
            ],
            [
                "https://twitter.com/telltalegames",
                "Twitter"
            ],
            [
                "https://www.youtube.com/user/TelltaleGames",
                "YouTube"
            ],
            [
                "https://store.steampowered.com/app/579950",
                "Steam"
            ],
            [
                "https://www.gog.com/game/guardians_of_the_galaxy",
                "GOG"
            ],
            [
                "https://telltale.com/series/guardiansofthegalaxy",
                "Official"
            ],
            [
                "https://www.twitch.tv/directory/game/Guardians%20of%20the%20Galaxy:%20The%20Telltale%20Series",
                "Twitch"
            ]
        ])
        self.assertEqual(first_result['main_story'], 8.81)
        self.assertEqual(first_result['main_extra'], 9.81)
        self.assertEqual(first_result['completionist'], 9.85)
        self.assertEqual(first_result['aggregated_rating'], 69.025)
        self.assertEqual(first_result['aggregated_rating_count'], 6)
        self.assertEqual(first_result['rating'], 70.4404)
        self.assertEqual(first_result['rating_count'], 67)
        self.assertEqual(first_result['release_dates'], "2017-04-18")
        self.assertEqual(first_result['storyline'], None)
        self.assertEqual(first_result['unclean_name'], "Marvel's Guardians of the Galaxy: The Telltale Series")
        self.assertEqual(first_result['unclean_summary'], "Marvel's Guardians of the Galaxy: The Telltale Series is a "
                                                          "brand new story of the universe's unlikeliest heroes: "
                                                          "Star-Lord, Gamora, Drax, Rocket, and Groot. In the wake of "
                                                          "an epic battle, the Guardians discover an artifact of "
                                                          "unspeakable power. Each of them has a reason to desire "
                                                          "this relic, as does a ruthless enemy who is the last of "
                                                          "her kind, and who will stop at nothing to tear it from "
                                                          "their hands.\n\nFrom Earth to the Milano to Knowhere and "
                                                          "beyond, and set to the beat of awesome music, you wear the "
                                                          "rocket-powered boots of Star-Lord in an original Guardians "
                                                          "adventure, where your decisions and actions drive the "
                                                          "story you experience.")
        self.assertEqual(first_result['popularity'], 0.760862)

    def test_search_with_valid_query(self):
        # Define a valid query
        valid_query = "the witcher"

        # Prepare a request with the valid query
        response = self.app.post('/game/search', data=json.dumps({'query': valid_query}),
                                 content_type='application/json')

        # Check the response status code
        self.assertEqual(response.status_code, 200)

    def test_search_with_null_query(self):
        # Prepare a request with a null query
        response = self.app.post('/game/search', data=json.dumps({'query': None}),
                                 content_type='application/json')

        # Check the response status code for a null query
        self.assertEqual(response.status_code, 400)

        # Check the response content to ensure it contains the expected error message
        response_data = json.loads(response.data)
        self.assertEqual(response_data['error'], 'Query cannot be null')


if __name__ == '__main__':
    unittest.main()
