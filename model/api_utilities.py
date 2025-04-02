import requests

def get_movie_details(movie_id, api_url="http://movie_api.com/movie/"):
    try:
        response = requests.get(f"{api_url}{movie_id}")
        if response.status_code == 200:
            return response.json()
        print(f"Error {response.status_code} fetching movie: {movie_id}")
    except Exception as e:
        print(f"Request failed: {e}")
    return None

def get_user_details(user_id, api_url="http://user_api.com/user/"):
    try:
        response = requests.get(f"{api_url}{user_id}")
        if response.status_code == 200:
            return response.json()
        print(f"Error {response.status_code} fetching user: {user_id}")
    except Exception as e:
        print(f"Request failed: {e}")
    return None
