# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
INITIAL_DISTEMPER_LEVEL = 1
INITIAL_TURQUET_SCORE = 100  # Arbitrary constant score for initialization
TERMED_FLAG_THRESHOLD = 10  # Arbitrary threshold for termed flag adjustment

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including 'distemper level' (a measure of how frequently an item is accessed), 'turquet score' (a random score assigned to each item), 'boilermaker index' (a measure of the item's age in the cache), and 'termed flag' (indicating if an item is nearing its eviction threshold).
metadata = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first considering items with the highest 'termed flag'. If multiple items have the same 'termed flag', it then considers the lowest 'distemper level'. If there is still a tie, it evicts the item with the lowest 'turquet score'.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    max_termed_flag = -1
    min_distemper_level = float('inf')
    min_turquet_score = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        obj_metadata = metadata[key]
        termed_flag = obj_metadata['termed_flag']
        distemper_level = obj_metadata['distemper_level']
        turquet_score = obj_metadata['turquet_score']

        if termed_flag > max_termed_flag:
            max_termed_flag = termed_flag
            min_distemper_level = distemper_level
            min_turquet_score = turquet_score
            candid_obj_key = key
        elif termed_flag == max_termed_flag:
            if distemper_level < min_distemper_level:
                min_distemper_level = distemper_level
                min_turquet_score = turquet_score
                candid_obj_key = key
            elif distemper_level == min_distemper_level:
                if turquet_score < min_turquet_score:
                    min_turquet_score = turquet_score
                    candid_obj_key = key

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy increases the 'distemper level' of the accessed item, recalculates its 'turquet score' randomly, and resets its 'boilermaker index' to zero. The 'termed flag' is adjusted based on the new 'distemper level'.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata[key]['distemper_level'] += 1
    metadata[key]['turquet_score'] = INITIAL_TURQUET_SCORE  # No randomness, use constant
    metadata[key]['boilermaker_index'] = 0
    metadata[key]['termed_flag'] = metadata[key]['distemper_level'] // TERMED_FLAG_THRESHOLD

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object into the cache, the policy assigns an initial 'distemper level' of one, a random 'turquet score', sets the 'boilermaker index' to zero, and initializes the 'termed flag' based on the insertion time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata[key] = {
        'distemper_level': INITIAL_DISTEMPER_LEVEL,
        'turquet_score': INITIAL_TURQUET_SCORE,  # No randomness, use constant
        'boilermaker_index': 0,
        'termed_flag': cache_snapshot.access_count // TERMED_FLAG_THRESHOLD
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting the victim, the policy recalculates the 'termed flag' for remaining items, adjusts their 'boilermaker index' by incrementing it, and may slightly increase the 'distemper level' of items that were not evicted to reflect their continued presence in the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in metadata:
        del metadata[evicted_key]

    for key, cached_obj in cache_snapshot.cache.items():
        metadata[key]['boilermaker_index'] += 1
        metadata[key]['distemper_level'] += 0.1  # Slight increase
        metadata[key]['termed_flag'] = metadata[key]['distemper_level'] // TERMED_FLAG_THRESHOLD