# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below

# Put the metadata specifically maintained by the policy below. The policy maintains a counter and a timestamp for each cache object, as well as a global cycle counter that increments with each cache cycle.
metadata = {
    'counters': {},  # Dictionary to store counters for each object
    'timestamps': {},  # Dictionary to store timestamps for each object
    'global_cycle_counter': 0  # Global cycle counter
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on the object with the highest counter value divided by the time since it was last accessed, aiming to balance between frequently and recently used objects.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_ratio = -1

    for key, cached_obj in cache_snapshot.cache.items():
        counter = metadata['counters'][key]
        last_access_time = metadata['timestamps'][key]
        time_since_last_access = cache_snapshot.access_count - last_access_time
        ratio = counter / time_since_last_access

        if ratio > max_ratio:
            max_ratio = ratio
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the counter for the accessed object is incremented and its timestamp is updated to the current time. The global cycle counter is also incremented.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['counters'][key] += 1
    metadata['timestamps'][key] = cache_snapshot.access_count
    metadata['global_cycle_counter'] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    When a new object is inserted, its counter is initialized to 1 and its timestamp is set to the current time. The global cycle counter is incremented.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['counters'][key] = 1
    metadata['timestamps'][key] = cache_snapshot.access_count
    metadata['global_cycle_counter'] += 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the global cycle counter is incremented. The evicted object's metadata is cleared from the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['counters']:
        del metadata['counters'][evicted_key]
    if evicted_key in metadata['timestamps']:
        del metadata['timestamps'][evicted_key]
    metadata['global_cycle_counter'] += 1