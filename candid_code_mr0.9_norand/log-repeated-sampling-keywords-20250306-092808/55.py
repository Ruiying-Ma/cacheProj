# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for frequency count
BETA = 0.3   # Weight for recency of access
GAMMA = 0.2  # Weight for pattern score

# Put the metadata specifically maintained by the policy below. The policy maintains a frequency count for each cached object, a timestamp of the last access, and a pattern score that reflects the regularity of access patterns.
metadata = {
    'frequency': {},  # Frequency count for each object
    'last_access': {},  # Last access timestamp for each object
    'pattern_score': {},  # Pattern score for each object
}

def calculate_combined_score(key, current_time):
    freq = metadata['frequency'].get(key, 0)
    last_access = metadata['last_access'].get(key, 0)
    pattern_score = metadata['pattern_score'].get(key, 0)
    recency = current_time - last_access
    combined_score = ALPHA * freq + BETA * recency + GAMMA * pattern_score
    return combined_score

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a combined score derived from the frequency count, recency of access, and pattern score. The object with the lowest combined score is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    current_time = cache_snapshot.access_count

    for key in cache_snapshot.cache:
        score = calculate_combined_score(key, current_time)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the frequency count of the accessed object is incremented, the last access timestamp is updated to the current time, and the pattern score is recalculated based on the new access interval.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count

    # Update frequency count
    metadata['frequency'][key] = metadata['frequency'].get(key, 0) + 1

    # Update last access timestamp
    last_access = metadata['last_access'].get(key, current_time)
    metadata['last_access'][key] = current_time

    # Update pattern score
    access_interval = current_time - last_access
    metadata['pattern_score'][key] = (metadata['pattern_score'].get(key, 0) + access_interval) / 2

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its frequency count is initialized to 1, the last access timestamp is set to the current time, and the pattern score is initialized based on the initial access interval.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count

    # Initialize frequency count
    metadata['frequency'][key] = 1

    # Initialize last access timestamp
    metadata['last_access'][key] = current_time

    # Initialize pattern score
    metadata['pattern_score'][key] = 0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the metadata for the evicted object is removed from the cache, and the combined scores for remaining objects are recalculated if necessary to maintain accurate eviction criteria.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key

    # Remove metadata for the evicted object
    if evicted_key in metadata['frequency']:
        del metadata['frequency'][evicted_key]
    if evicted_key in metadata['last_access']:
        del metadata['last_access'][evicted_key]
    if evicted_key in metadata['pattern_score']:
        del metadata['pattern_score'][evicted_key]

    # No need to recalculate combined scores as they are calculated on-the-fly in evict function