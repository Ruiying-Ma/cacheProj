# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
MISS_PENALTY_INCREMENT = 1
DIRTY_BIT_WRITE_THROUGH = False  # Assuming write-through policy is not used

# Put the metadata specifically maintained by the policy below. The policy maintains the following metadata for each cache line: access frequency, last access timestamp, dirty bit, and a miss penalty counter that increments on each miss.
metadata = {
    'access_frequency': {},
    'last_access_timestamp': {},
    'dirty_bit': {},
    'miss_penalty_counter': 0
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a weighted score that combines low access frequency, old access timestamp, and high miss penalty counter. Dirty lines are deprioritized for eviction to minimize write-through penalties.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_freq = metadata['access_frequency'].get(key, 0)
        last_access = metadata['last_access_timestamp'].get(key, 0)
        dirty_bit = metadata['dirty_bit'].get(key, False)
        
        # Calculate the score for eviction
        score = (1 / (access_freq + 1)) + (cache_snapshot.access_count - last_access) + (metadata['miss_penalty_counter'])
        
        # Deprioritize dirty lines
        if dirty_bit:
            score += 1000  # Arbitrary large number to deprioritize
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the access frequency is incremented, the last access timestamp is updated to the current time, and the miss penalty counter is reset to zero.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_timestamp'][key] = cache_snapshot.access_count
    metadata['miss_penalty_counter'] = 0

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the access frequency is initialized to one, the last access timestamp is set to the current time, the dirty bit is set based on the write-through policy, and the miss penalty counter is reset to zero.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_timestamp'][key] = cache_snapshot.access_count
    metadata['dirty_bit'][key] = not DIRTY_BIT_WRITE_THROUGH
    metadata['miss_penalty_counter'] = 0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the miss penalty counter for the cache is incremented, and the metadata for the evicted line is cleared or reinitialized for the new incoming line.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    metadata['miss_penalty_counter'] += MISS_PENALTY_INCREMENT
    
    # Clear metadata for the evicted object
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['last_access_timestamp']:
        del metadata['last_access_timestamp'][evicted_key]
    if evicted_key in metadata['dirty_bit']:
        del metadata['dirty_bit'][evicted_key]