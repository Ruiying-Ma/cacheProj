# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
SYMBOLIC_WEIGHT_INCREMENT = 1
ADLEGIARE_SCORE_INCREMENT = 1
UNRULY_INDEX_DECREMENT = 1
INITIAL_SYMBOLIC_WEIGHT = 10
INITIAL_ADLEGIARE_SCORE = 5
INITIAL_UNRULY_INDEX = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a 'symbolic weight' for each cache entry, an 'adlegiare score' representing the entry's adaptability, and an 'unruly index' indicating the entry's tendency to disrupt cache stability.
symbolic_weights = {}
adlegiare_scores = {}
unruly_indexes = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the highest unruly index, then considering the symbolic weight and adlegiare score to ensure a balanced cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    max_unruly_index = -1
    for key in cache_snapshot.cache:
        if unruly_indexes[key] > max_unruly_index:
            max_unruly_index = unruly_indexes[key]
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the symbolic weight of the accessed entry is increased slightly, the adlegiare score is adjusted to reflect improved adaptability, and the unruly index is decreased to indicate stabilized behavior.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    symbolic_weights[key] += SYMBOLIC_WEIGHT_INCREMENT
    adlegiare_scores[key] += ADLEGIARE_SCORE_INCREMENT
    unruly_indexes[key] -= UNRULY_INDEX_DECREMENT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the symbolic weight is initialized based on the object's importance, the adlegiare score is set to a neutral value, and the unruly index is set to a low value to start with stable behavior.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    symbolic_weights[key] = INITIAL_SYMBOLIC_WEIGHT
    adlegiare_scores[key] = INITIAL_ADLEGIARE_SCORE
    unruly_indexes[key] = INITIAL_UNRULY_INDEX

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting the victim, the symbolic weights of remaining entries are recalibrated to maintain balance, the adlegiare scores are adjusted to reflect the new cache composition, and the unruly indexes are normalized to ensure overall cache stability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    del symbolic_weights[evicted_key]
    del adlegiare_scores[evicted_key]
    del unruly_indexes[evicted_key]
    
    total_weight = sum(symbolic_weights.values())
    total_adlegiare = sum(adlegiare_scores.values())
    total_unruly = sum(unruly_indexes.values())
    
    for key in cache_snapshot.cache:
        symbolic_weights[key] = symbolic_weights[key] / total_weight * len(symbolic_weights)
        adlegiare_scores[key] = adlegiare_scores[key] / total_adlegiare * len(adlegiare_scores)
        unruly_indexes[key] = unruly_indexes[key] / total_unruly * len(unruly_indexes)