import pandas as pd
from datetime import datetime

# Load the CSV file
file_path = "backend/model/ratings.csv"
df = pd.read_csv(file_path)

# Function to correct errors
def clean_data(row):
    # Check timestamp
    try:
        row['timestamp'] = datetime.strptime(row['timestamp'], "%Y-%m-%dT%H:%M:%S").isoformat()
    except (ValueError, TypeError):
        print('Wrong datetime format:'+row['timestamp'] + " -> " + row['timestamp']+":00")
        row['timestamp'] = row['timestamp']+":00"  # Default timestamp for errors

    # Check user_id
    if not isinstance(row['user_id'], int) or pd.isna(row['user_id']):
        print("User ID is not known, changed to -1")
        row['user_id'] = -1  # Placeholder for invalid/missing user_id
    
    # Check movie_id
    if not isinstance(row['movie_id'], str) or pd.isna(row['movie_id']):
        print('Movie ID is not known, changed to "Unknown Movie"')
        row['movie_id'] = "unknown_movie"
    
    # Check rating
    try:
        row['rating'] = int(row['rating'])
        if row['rating'] < 0 or row['rating'] > 5:
            row['rating'] = 3  # Default to 3 if rating is out of range
    except (ValueError, TypeError):
        return None  # Mark row for deletion if rating is missing or invalid
    
    return row

# Apply the cleaning function
df = df.apply(clean_data, axis=1)

# Remove rows where rating is missing or invalid
if len(df)!=len(df.dropna().reset_index(drop=False)):
    print("Some rows with ratings missing! Dropping those!")
    df = df.dropna().reset_index(drop=True)

# Save the cleaned file
print("File's cleaned now!!")
df.to_csv("backend/model/cleaned_ratings.csv", index=False)
