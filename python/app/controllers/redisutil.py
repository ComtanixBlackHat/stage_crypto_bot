import redis
import json

class RedisUtility:
    # Static Redis client
    _client = redis.StrictRedis(
        host="localhost",
        port=6379,
        db=0,
        password=None,
        decode_responses=True  # Decodes bytes to strings automatically
    )

    @staticmethod
    def set_key(key, value, expire=None):
        """
        Set a key-value pair in Redis.
        :param key: Key name.
        :param value: Value to store.
        :param expire: Expiration time in seconds (optional).
        """
        if isinstance(value, (dict, list)):
            value = json.dumps(value)  # Serialize JSON-compatible data
        RedisUtility._client.set(key, value, ex=expire)

    @staticmethod
    def get_key(key):
        """
        Get the value of a key.
        :param key: Key name.
        :return: Value of the key or None if key does not exist.
        """
        value = RedisUtility._client.get(key)
        try:
            return json.loads(value)  # Deserialize JSON if applicable
        except (TypeError, json.JSONDecodeError):
            return value

    @staticmethod
    def delete_key(key):
        """
        Delete a key from Redis.
        :param key: Key name.
        :return: Number of keys deleted (0 or 1).
        """
        return RedisUtility._client.delete(key)

    @staticmethod
    def increment_key(key, amount=1):
        """
        Increment the value of a key by a given amount.
        :param key: Key name.
        :param amount: Amount to increment (default: 1).
        :return: New value of the key.
        """
        return RedisUtility._client.incr(key, amount)

    @staticmethod
    def decrement_key(key, amount=1):
        """
        Decrement the value of a key by a given amount.
        :param key: Key name.
        :param amount: Amount to decrement (default: 1).
        :return: New value of the key.
        """
        return RedisUtility._client.decr(key, amount)

    @staticmethod
    def set_hash(name, mapping):
        """
        Set multiple fields in a hash.
        :param name: Hash name.
        :param mapping: Dictionary of fields and values to store.
        """
        RedisUtility._client.hset(name, mapping=mapping)


    @staticmethod
    def set_hash_field(hash_name, field, value):
        """
        Set an individual field in a Redis hash.
        :param hash_name: Name of the Redis hash.
        :param field: The field name to set.
        :param value: The value to store in the field.
        """
        RedisUtility._client.hset(hash_name, field, value)


    @staticmethod
    def get_all_hash_fields(hash_name):
        """
        Retrieve all fields and values from a Redis hash.
        :param hash_name: Name of the Redis hash.
        :return: Dictionary of all fields and their values.
        """
        return RedisUtility._client.hgetall(hash_name)
   
    @staticmethod
    def get_hash_field(hash_name, key):
        """
        Retrieve a specific field value from a Redis hash.
        :param hash_name: Name of the Redis hash.
        :param key: The field key within the hash.
        :return: Value of the specified field or None if not found.
        """
        return RedisUtility._client.hget(hash_name, key)

    @staticmethod
    def get_hash(name):
        """
        Get all fields and values of a hash.
        :param name: Hash name.
        :return: Dictionary of fields and values.
        """
        return RedisUtility._client.hgetall(name)

    @staticmethod
    def delete_hash_field(name, field):
        """
        Delete a field from a hash.
        :param name: Hash name.
        :param field: Field name.
        :return: Number of fields removed (0 or 1).
        """
        return RedisUtility._client.hdel(name, field)

    @staticmethod
    def push_to_list(name, value):
        """
        Push a value to a Redis list (right push).
        :param name: List name.
        :param value: Value to push.
        """
        RedisUtility._client.rpush(name, value)

    @staticmethod
    def pop_from_list(name):
        """
        Pop a value from a Redis list (left pop).
        :param name: List name.
        :return: Popped value.
        """
        return RedisUtility._client.lpop(name)

    @staticmethod
    def get_list(name):
        """
        Get all elements of a Redis list.
        :param name: List name.
        :return: List of values.
        """
        return RedisUtility._client.lrange(name, 0, -1)

    @staticmethod
    def set_add(name, value):
        """
        Add a value to a Redis set.
        :param name: Set name.
        :param value: Value to add.
        """
        RedisUtility._client.sadd(name, value)

    @staticmethod
    def get_set(name):
        """
        Get all members of a Redis set.
        :param name: Set name.
        :return: Set of values.
        """
        return RedisUtility._client.smembers(name)

    @staticmethod
    def delete_set_member(name, value):
        """
        Remove a member from a Redis set.
        :param name: Set name.
        :param value: Member to remove.
        """
        RedisUtility._client.srem(name, value)

    @staticmethod
    def key_exists(key):
        """
        Check if a key exists in Redis.
        :param key: Key name.
        :return: True if key exists, False otherwise.
        """
        return RedisUtility._client.exists(key) > 0

    @staticmethod
    def flush_db():
        """
        Delete all keys in the current database.
        """
        RedisUtility._client.flushdb()

    @staticmethod
    def flush_all():
        """
        Delete all keys in all databases.
        """
        RedisUtility._client.flushall()
