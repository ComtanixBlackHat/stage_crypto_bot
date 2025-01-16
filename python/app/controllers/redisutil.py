import redis
import json

class RedisUtility:
    def __init__(self, host="localhost", port=6379, db=0, password=None):
        """
        Initialize a connection to the Redis database.
        :param host: Redis server hostname.
        :param port: Redis server port.
        :param db: Redis database index.
        :param password: Redis server password (if required).
        """
        self.client = redis.StrictRedis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True  # Decodes bytes to strings automatically
        )

    def set_key(self, key, value, expire=None):
        """
        Set a key-value pair in Redis.
        :param key: Key name.
        :param value: Value to store.
        :param expire: Expiration time in seconds (optional).
        """
        if isinstance(value, (dict, list)):
            value = json.dumps(value)  # Serialize JSON-compatible data
        self.client.set(key, value, ex=expire)

    def get_key(self, key):
        """
        Get the value of a key.
        :param key: Key name.
        :return: Value of the key or None if key does not exist.
        """
        value = self.client.get(key)
        try:
            return json.loads(value)  # Deserialize JSON if applicable
        except (TypeError, json.JSONDecodeError):
            return value

    def delete_key(self, key):
        """
        Delete a key from Redis.
        :param key: Key name.
        :return: Number of keys deleted (0 or 1).
        """
        return self.client.delete(key)

    def increment_key(self, key, amount=1):
        """
        Increment the value of a key by a given amount.
        :param key: Key name.
        :param amount: Amount to increment (default: 1).
        :return: New value of the key.
        """
        return self.client.incr(key, amount)

    def decrement_key(self, key, amount=1):
        """
        Decrement the value of a key by a given amount.
        :param key: Key name.
        :param amount: Amount to decrement (default: 1).
        :return: New value of the key.
        """
        return self.client.decr(key, amount)

    def set_hash(self, name, mapping):
        """
        Set multiple fields in a hash.
        :param name: Hash name.
        :param mapping: Dictionary of fields and values to store.
        """
        self.client.hset(name, mapping=mapping)

    def get_hash(self, name):
        """
        Get all fields and values of a hash.
        :param name: Hash name.
        :return: Dictionary of fields and values.
        """
        return self.client.hgetall(name)

    def delete_hash_field(self, name, field):
        """
        Delete a field from a hash.
        :param name: Hash name.
        :param field: Field name.
        :return: Number of fields removed (0 or 1).
        """
        return self.client.hdel(name, field)

    def push_to_list(self, name, value):
        """
        Push a value to a Redis list (right push).
        :param name: List name.
        :param value: Value to push.
        """
        self.client.rpush(name, value)

    def pop_from_list(self, name):
        """
        Pop a value from a Redis list (left pop).
        :param name: List name.
        :return: Popped value.
        """
        return self.client.lpop(name)

    def get_list(self, name):
        """
        Get all elements of a Redis list.
        :param name: List name.
        :return: List of values.
        """
        return self.client.lrange(name, 0, -1)

    def set_add(self, name, value):
        """
        Add a value to a Redis set.
        :param name: Set name.
        :param value: Value to add.
        """
        self.client.sadd(name, value)

    def get_set(self, name):
        """
        Get all members of a Redis set.
        :param name: Set name.
        :return: Set of values.
        """
        return self.client.smembers(name)

    def delete_set_member(self, name, value):
        """
        Remove a member from a Redis set.
        :param name: Set name.
        :param value: Member to remove.
        """
        self.client.srem(name, value)

    def key_exists(self, key):
        """
        Check if a key exists in Redis.
        :param key: Key name.
        :return: True if key exists, False otherwise.
        """
        return self.client.exists(key) > 0

    def flush_db(self):
        """
        Delete all keys in the current database.
        """
        self.client.flushdb()

    def flush_all(self):
        """
        Delete all keys in all databases.
        """
        self.client.flushall()
