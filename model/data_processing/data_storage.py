import pandas as pd

def save_to_csv(data, filename, columns):
    if not data:
        print(f"No data to save in {filename}")
        return
    
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(filename, index=False)
    print(f"Saved {filename}")

if __name__ == "__main__":
    sample_data = [("2025-03-13 10:00:00", "user123", "movie456", 4)]
    save_to_csv(sample_data, "ratings.csv", ["timestamp", "user_id", "movie_id", "rating"])
