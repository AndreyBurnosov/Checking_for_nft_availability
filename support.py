import redis
from pytonconnect.storage import IStorage

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

class Storage(IStorage):
    def __init__(self, id):
        self.id = id
    
    async def set_item(self, key: str, value: str):
        r.set(key + self.id, value)

    async def get_item(self, key: str, default_value: str = None):
        if r.exists(key + self.id):
            return r.get(key + self.id)
        else:
            return default_value
    
    async def remove_item(self, key: str):
        r.delete(key + self.id)