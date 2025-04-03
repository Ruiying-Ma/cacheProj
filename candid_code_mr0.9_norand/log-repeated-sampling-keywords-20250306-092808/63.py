# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below

# Put the metadata specifically maintained by the policy below. The policy maintains a hash map to track access patterns, a counter for each key to record access frequency, and a timestamp for each key to record the last access time. It also keeps track of the total cache size and the number of items currently in the cache.
access_frequency = {}
last_access_time = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a combination of the least frequently used (LFU) and the least recently used (LRU) metrics. It calculates a score for each key by combining the access frequency and the time since the last access, and evicts the key with the lowest score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        frequency = access_frequency.get(key, 0)
        last_access = last_access_time.get(key, 0)
        score = frequency + (cache_snapshot.access_count - last_access)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the access frequency counter for the key and updates the timestamp to the current time. It also updates the hash map to reflect the new access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] = access_frequency.get(key, 0) + 1
    last_access_time[key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency counter to 1 and sets the timestamp to the current time. It updates the hash map to include the new key and adjusts the total cache size and item count accordingly.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] = 1
    last_access_time[key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes the key from the hash map, resets its access frequency counter and timestamp, and updates the total cache size and item count to reflect the removal.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in access_frequency:
        del access_frequency[evicted_key]
    if evicted_key in last_access_time:
        del last_access_time[evicted_key]