# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
INITIAL_DECAY_FACTOR = 1.0
INITIAL_LIFETIME = 100

# Put the metadata specifically maintained by the policy below. The policy maintains a recency-bit for each object, a temporal decay factor, and an estimated object lifetime. The recency-bit tracks recent access, the temporal decay factor reduces the importance of older accesses over time, and the object lifetime estimates how long an object is expected to stay relevant.
metadata = {
    'recency_bit': {},  # {obj.key: recency_bit}
    'decay_factor': {},  # {obj.key: decay_factor}
    'lifetime': {}  # {obj.key: lifetime}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the object with the lowest combined score of recency-bit, temporal decay, and remaining estimated lifetime. Objects with a recency-bit of 0, high temporal decay, and short remaining lifetime are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        recency_bit = metadata['recency_bit'].get(key, 0)
        decay_factor = metadata['decay_factor'].get(key, INITIAL_DECAY_FACTOR)
        lifetime = metadata['lifetime'].get(key, INITIAL_LIFETIME)
        
        score = (1 - recency_bit) + decay_factor + (INITIAL_LIFETIME - lifetime)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the recency-bit of the accessed object is set to 1, the temporal decay factor is reset to its initial value, and the estimated object lifetime is recalculated based on the current access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['recency_bit'][key] = 1
    metadata['decay_factor'][key] = INITIAL_DECAY_FACTOR
    metadata['lifetime'][key] = INITIAL_LIFETIME

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its recency-bit is set to 1, the temporal decay factor is initialized to a default value, and the estimated object lifetime is set based on initial predictions or heuristics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['recency_bit'][key] = 1
    metadata['decay_factor'][key] = INITIAL_DECAY_FACTOR
    metadata['lifetime'][key] = INITIAL_LIFETIME

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy recalculates the temporal decay factors for all remaining objects to ensure they reflect the current state of the cache, and adjusts the estimated lifetimes if necessary to maintain accurate predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        if key in metadata['decay_factor']:
            metadata['decay_factor'][key] *= 0.9  # Example decay adjustment
        if key in metadata['lifetime']:
            metadata['lifetime'][key] -= 1  # Example lifetime adjustment