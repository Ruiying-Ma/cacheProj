# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
BASELINE_HYPERCYANOTIC_SCORE = 10

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency, and a unique 'hypercyanotic' score that increases with consecutive hits and decreases with misses. It also tracks 'verbalization' patterns, which are sequences of access patterns, and 'underseas' depth, which measures the depth of the cache hierarchy where the object resides.
metadata = {
    'access_frequency': {},
    'recency': {},
    'hypercyanotic_score': {},
    'verbalization_pattern': {},
    'underseas_depth': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on the lowest combined score of access frequency, recency, hypercyanotic score, verbalization pattern match, and underseas depth. Objects with the least recent access and lowest hypercyanotic score are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    lowest_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (
            metadata['access_frequency'][key] +
            cache_snapshot.access_count - metadata['recency'][key] +
            metadata['hypercyanotic_score'][key] +
            len(metadata['verbalization_pattern'][key]) +
            metadata['underseas_depth'][key]
        )
        
        if combined_score < lowest_score:
            lowest_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency by incrementing it, increases the hypercyanotic score, updates the recency timestamp, and adjusts the verbalization pattern to reflect the latest access sequence. The underseas depth remains unchanged.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['hypercyanotic_score'][key] += 1
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['verbalization_pattern'][key].append(cache_snapshot.access_count)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the hypercyanotic score to a baseline value, records the current timestamp for recency, starts a new verbalization pattern, and assigns an initial underseas depth based on its position in the cache hierarchy.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['hypercyanotic_score'][key] = BASELINE_HYPERCYANOTIC_SCORE
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['verbalization_pattern'][key] = [cache_snapshot.access_count]
    metadata['underseas_depth'][key] = len(cache_snapshot.cache)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes all associated metadata for the evicted object, recalibrates the hypercyanotic scores of remaining objects to prevent inflation, updates verbalization patterns to reflect the removal, and adjusts underseas depths to maintain cache hierarchy integrity.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del metadata['access_frequency'][evicted_key]
    del metadata['recency'][evicted_key]
    del metadata['hypercyanotic_score'][evicted_key]
    del metadata['verbalization_pattern'][evicted_key]
    del metadata['underseas_depth'][evicted_key]
    
    for key in cache_snapshot.cache.keys():
        metadata['hypercyanotic_score'][key] = max(BASELINE_HYPERCYANOTIC_SCORE, metadata['hypercyanotic_score'][key] - 1)
        metadata['verbalization_pattern'][key] = [timestamp for timestamp in metadata['verbalization_pattern'][key] if timestamp != cache_snapshot.access_count]
        metadata['underseas_depth'][key] = len(cache_snapshot.cache)