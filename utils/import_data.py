import pandas as pd
from sqlalchemy import create_engine

def import_csv_to_mysql(csv_file_path):
    # Define the MySQL database connection URL
    db_url = 'mysql://root:password@localhost/gamity'

    # Create a SQLAlchemy engine
    engine = create_engine(db_url)

    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_file_path)

        # Ensure that the DataFrame columns match the table columns
        df.columns = ['game_id', 'recommended_game_id', 'composite_score']

        # Insert the DataFrame data into the MySQL table
        df.to_sql('recommendation', con=engine, if_exists='append', index=False)

        print(f"Data from {csv_file_path} successfully imported into MySQL.")
    except Exception as e:
        print(f"Error: {e}")

# Example usage:
csv_file_path = '../assets/all_recommendations055.csv'
import_csv_to_mysql(csv_file_path)