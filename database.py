# Importing the Redis library to interact with the Redis database
import redis
# Importing the IStorage interface from pytonconnect
from pytonconnect.storage import IStorage

# Creating a connection to the Redis database running on localhost at port 6379
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Defining a class Storage that implements the IStorage interface from pytonconnect
class Storage(IStorage):
    def __init__(self, id):
        # Constructor method initializing the unique identifier for each storage instance
        self.id = id
    
    # Asynchronous method to set a key-value pair in Redis, with the key being appended with the unique ID
    async def set_item(self, key: str, value: str):
        r.set(key + self.id, value)

    # Asynchronous method to retrieve the value for a given key from Redis, with the key being appended with the unique ID
    # If the key does not exist, returns the default value
    async def get_item(self, key: str, default_value: str = None):
        if r.exists(key + self.id):
            return r.get(key + self.id)
        else:
            return default_value
    
    # Asynchronous method to remove the key-value pair for a given key from Redis, with the key being appended with the unique ID
    async def remove_item(self, key: str):
        r.delete(key + self.id)
