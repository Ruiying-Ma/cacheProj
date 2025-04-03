# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
SEQUENTIAL_PENALTY = 1
RANDOM_PENALTY = 2

# Put the metadata specifically maintained by the policy below. Maintains a list of cache entries with timestamps for insertion, an access frequency counter, and a simple access pattern tag (sequential or random), as well as the size of each entry.
cache_metadata = {
    'timestamps': {},  # {key: timestamp}
    'access_frequency': {},  # {key: frequency}
    'access_pattern': {},  # {key: 'sequential' or 'random'}
    'sizes': {}  # {key: size}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    Chooses the eviction victim based on a composite score that considers the least frequently used entries with the oldest timestamps and penalizes sequential access patterns less compared to random patterns, adjusted by the size of entries to ensure efficient use of cache space.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        frequency = cache_metadata['access_frequency'][key]
        timestamp = cache_metadata['timestamps'][key]
        pattern = cache_metadata['access_pattern'][key]
        size = cache_metadata['sizes'][key]
        
        pattern_penalty = SEQUENTIAL_PENALTY if pattern == 'sequential' else RANDOM_PENALTY
        score = (frequency * pattern_penalty) + (cache_snapshot.access_count - timestamp) + size
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Increments the access frequency counter for the hit entry, updates its access pattern tag based on the previous access, and records the current timestamp.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    cache_metadata['access_frequency'][key] += 1
    cache_metadata['timestamps'][key] = cache_snapshot.access_count
    
    # Update access pattern
    if cache_metadata['access_pattern'][key] == 'sequential':
        cache_metadata['access_pattern'][key] = 'random'
    else:
        cache_metadata['access_pattern'][key] = 'sequential'

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    Adds the new object to the list, initializes its access frequency counter to 1, assigns a timestamp for insertion, and tags its initial access pattern. Adjusts entry sizes accordingly.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    cache_metadata['timestamps'][key] = cache_snapshot.access_count
    cache_metadata['access_frequency'][key] = 1
    cache_metadata['access_pattern'][key] = 'sequential'
    cache_metadata['sizes'][key] = obj.size

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Removes the evicted entry from the list and reclaims its space in the cache. No direct impact on the existing entries' metadata.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    del cache_metadata['timestamps'][key]
    del cache_metadata['access_frequency'][key]
    del cache_metadata['access_pattern'][key]
    del cache_metadata['sizes'][key]