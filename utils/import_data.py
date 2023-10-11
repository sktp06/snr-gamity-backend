import pandas as pd
from sqlalchemy import create_engine


# def import_recommendations055():
#     # Fixed MySQL database connection URL
#     db_url = 'mysql://root:password@localhost/gamity'
#
#     # Create a SQLAlchemy engine
#     engine = create_engine(db_url)
#
#     try:
#         # Read the CSV file into a DataFrame
#         csv_file_path = '../assets/all_recommendations055.csv'
#         df = pd.read_csv(csv_file_path)
#
#         # Ensure that the DataFrame columns match the table columns
#         df.columns = ['game_id', 'recommended_game_id', 'composite_score']
#
#         # Insert the DataFrame data into the MySQL table
#         df.to_sql('recommendation', con=engine, if_exists='append', index=False)
#
#         print(f"Data from {csv_file_path} successfully imported into MySQL.")
#     except Exception as e:
#         print(f"Error: {e}")
#
#
# # Call the function to execute it
# import_recommendations055()


# def import_topGame():
#     # Fixed MySQL database connection URL
#     db_url = 'mysql://root:password@localhost/gamity'
#
#     # Create a SQLAlchemy engine
#     engine = create_engine(db_url)
#
#     try:
#         # Read the CSV file into a DataFrame
#         csv_file_path = '../assets/limit_games.csv'
#         df = pd.read_csv(csv_file_path)
#
#         # Ensure that the DataFrame columns match the table columns
#         df.columns = ['id',
#                       'cover',
#                       'genres',
#                       'name',
#                       'summary',
#                       'url',
#                       'websites',
#                       'main_story',
#                       'main_extra',
#                       'completionist',
#                       'aggregated_rating',
#                       'aggregated_rating_count',
#                       'rating',
#                       'rating_count',
#                       'release_dates',
#                       'storyline',
#                       'unclean_name',
#                       'unclean_summary',
#                       'popularity'
#                       ]
#
#         # Insert the DataFrame data into the MySQL table
#         df.to_sql('topGame', con=engine, if_exists='append', index=False)
#
#         print(f"Data from {csv_file_path} successfully imported into MySQL.")
#     except Exception as e:
#         print(f"Error: {e}")
#
#
# # Call the function to execute it
# import_topGame()

def import_upComingGame():
    # Fixed MySQL database connection URL
    db_url = 'mysql://root:password@localhost/gamity'

    # Create a SQLAlchemy engine
    engine = create_engine(db_url)

    try:
        # Read the CSV file into a DataFrame
        csv_file_path = '../assets/upcoming_games.csv'
        df = pd.read_csv(csv_file_path)

        # Ensure that the DataFrame columns match the table columns
        df.columns = ['id',
                      'cover',
                      'genres',
                      'name',
                      'summary',
                      'url',
                      'websites',
                      'main_story',
                      'main_extra',
                      'completionist',
                      'aggregated_rating',
                      'aggregated_rating_count',
                      'rating',
                      'rating_count',
                      'release_dates',
                      'storyline',
                      'unclean_name',
                      'unclean_summary',
                      'popularity'
                      ]

        # Insert the DataFrame data into the MySQL table
        df.to_sql('upComingGame', con=engine, if_exists='append', index=False)

        print(f"Data from {csv_file_path} successfully imported into MySQL.")
    except Exception as e:
        print(f"Error: {e}")


# Call the function to execute it
import_upComingGame()
