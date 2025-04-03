# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
DEFAULT_BRACKET_SCORE = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a 'bracket' score for each cache entry, a 'petal' count representing the frequency of access, a 'guest' flag indicating recent access, and a 'shirt' timestamp for the last access time.
metadata = {
    'bracket': {},  # key -> bracket score
    'petal': {},    # key -> petal count
    'guest': {},    # key -> guest flag
    'shirt': {}     # key -> shirt timestamp
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first considering entries with the lowest 'bracket' score. Among those, it selects the one with the lowest 'petal' count. If there is a tie, it evicts the entry with the 'guest' flag set to false. If still tied, it evicts the entry with the oldest 'shirt' timestamp.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_bracket = float('inf')
    min_petal = float('inf')
    oldest_shirt = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        bracket = metadata['bracket'][key]
        petal = metadata['petal'][key]
        guest = metadata['guest'][key]
        shirt = metadata['shirt'][key]

        if bracket < min_bracket or \
           (bracket == min_bracket and petal < min_petal) or \
           (bracket == min_bracket and petal == min_petal and not guest) or \
           (bracket == min_bracket and petal == min_petal and guest and shirt < oldest_shirt):
            min_bracket = bracket
            min_petal = petal
            oldest_shirt = shirt
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the 'bracket' score of the entry is incremented, the 'petal' count is increased by one, the 'guest' flag is set to true, and the 'shirt' timestamp is updated to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['bracket'][key] += 1
    metadata['petal'][key] += 1
    metadata['guest'][key] = True
    metadata['shirt'][key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the 'bracket' score to a default value, sets the 'petal' count to one, sets the 'guest' flag to true, and updates the 'shirt' timestamp to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['bracket'][key] = DEFAULT_BRACKET_SCORE
    metadata['petal'][key] = 1
    metadata['guest'][key] = True
    metadata['shirt'][key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy recalculates the 'bracket' scores of remaining entries to ensure balance, resets the 'guest' flag of all entries to false, and leaves the 'petal' counts and 'shirt' timestamps unchanged.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del metadata['bracket'][evicted_key]
    del metadata['petal'][evicted_key]
    del metadata['guest'][evicted_key]
    del metadata['shirt'][evicted_key]

    for key in cache_snapshot.cache.keys():
        metadata['bracket'][key] = max(DEFAULT_BRACKET_SCORE, metadata['bracket'][key] - 1)
        metadata['guest'][key] = False