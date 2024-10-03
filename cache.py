import time

CACHE_EXPIRATION_TIME = 300  # Cache expiration time in seconds (5 minutes)
cache = {}

# Cache checking function


def get_cached_response(query: str):
    current_time = time.time()
    if query in cache:
        response_data = cache[query]
        if current_time - response_data['timestamp'] < CACHE_EXPIRATION_TIME:
            return response_data['response']
        else:
            del cache[query]  # Remove expired cache entry
    return None

# Function to cache responses


def cache_response(query: str, response: str):
    cache[query] = {
        "response": response,
        "timestamp": time.time()
    }
