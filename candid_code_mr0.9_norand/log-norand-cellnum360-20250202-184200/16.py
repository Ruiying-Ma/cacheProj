# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
from collections import defaultdict, deque
import time

# Put tunable constant parameters below
SHARD_COUNT = 4  # Example shard count, can be adjusted based on requirements

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, shard identifier, and replication factor for each cached object. It also keeps track of the load and balance status of each shard.
metadata = {
    'access_frequency': defaultdict(int),
    'last_access_timestamp': defaultdict(int),
    'shard_identifier': {},
    'replication_factor': defaultdict(int),
    'shard_load': defaultdict(int),
    'shard_objects': defaultdict(set)
}

def get_shard_id(obj_key):
    return hash(obj_key) % SHARD_COUNT

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a combination of the least frequently accessed and the oldest timestamp within the most loaded shard. It ensures that the eviction does not disrupt the shard balance and considers replication factors to maintain data redundancy.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    most_loaded_shard = max(metadata['shard_load'], key=metadata['shard_load'].get)
    min_freq = float('inf')
    oldest_timestamp = float('inf')
    
    for obj_key in metadata['shard_objects'][most_loaded_shard]:
        if metadata['access_frequency'][obj_key] < min_freq or \
           (metadata['access_frequency'][obj_key] == min_freq and metadata['last_access_timestamp'][obj_key] < oldest_timestamp):
            min_freq = metadata['access_frequency'][obj_key]
            oldest_timestamp = metadata['last_access_timestamp'][obj_key]
            candid_obj_key = obj_key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency and last access timestamp of the accessed object. It also checks and updates the load status of the shard to ensure balanced distribution.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    obj_key = obj.key
    metadata['access_frequency'][obj_key] += 1
    metadata['last_access_timestamp'][obj_key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy updates the shard identifier and replication factor for the object. It also updates the load status of the shard and ensures that the new insertion maintains or improves shard balance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    obj_key = obj.key
    shard_id = get_shard_id(obj_key)
    metadata['shard_identifier'][obj_key] = shard_id
    metadata['replication_factor'][obj_key] += 1
    metadata['shard_load'][shard_id] += obj.size
    metadata['shard_objects'][shard_id].add(obj_key)
    metadata['access_frequency'][obj_key] = 1
    metadata['last_access_timestamp'][obj_key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy updates the load status of the shard from which the object was evicted. It also adjusts the replication factor metadata to ensure that data redundancy is maintained across the system.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_obj_key = evicted_obj.key
    shard_id = metadata['shard_identifier'][evicted_obj_key]
    metadata['shard_load'][shard_id] -= evicted_obj.size
    metadata['shard_objects'][shard_id].remove(evicted_obj_key)
    metadata['replication_factor'][evicted_obj_key] -= 1
    if metadata['replication_factor'][evicted_obj_key] == 0:
        del metadata['access_frequency'][evicted_obj_key]
        del metadata['last_access_timestamp'][evicted_obj_key]
        del metadata['shard_identifier'][evicted_obj_key]
        del metadata['replication_factor'][evicted_obj_key]