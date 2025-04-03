# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
INITIAL_SEMIGELATINOUS_SCORE = 50
SEMIGELATINOUS_INCREMENT = 5
SEMIGELATINOUS_ADJUSTMENT = -1

# Put the metadata specifically maintained by the policy below. The policy maintains a semigelatinous score for each cache entry, a bedark timestamp indicating the last access time, a berain counter tracking the frequency of access, and a Kickapoo flag indicating if the entry is part of a critical operation.
metadata = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on the lowest semigelatinous score, prioritizing entries with older bedark timestamps and lower berain counters, unless the Kickapoo flag is set, in which case those entries are protected from eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        if metadata[key]['kickapoo']:
            continue
        score = metadata[key]['semigelatinous_score']
        if score < min_score or (score == min_score and (metadata[key]['bedark'] < metadata[candid_obj_key]['bedark'] or metadata[key]['berain'] < metadata[candid_obj_key]['berain'])):
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the semigelatinous score of the accessed entry is slightly increased, the bedark timestamp is updated to the current time, the berain counter is incremented, and the Kickapoo flag remains unchanged.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata[key]['semigelatinous_score'] += SEMIGELATINOUS_INCREMENT
    metadata[key]['bedark'] = cache_snapshot.access_count
    metadata[key]['berain'] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the semigelatinous score is initialized to a medium value, the bedark timestamp is set to the current time, the berain counter starts at one, and the Kickapoo flag is set based on the criticality of the operation.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata[key] = {
        'semigelatinous_score': INITIAL_SEMIGELATINOUS_SCORE,
        'bedark': cache_snapshot.access_count,
        'berain': 1,
        'kickapoo': False  # Assuming a default value for criticality
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the semigelatinous scores of remaining entries are slightly adjusted to reflect the new cache state, bedark timestamps remain unchanged, berain counters are unaffected, and Kickapoo flags are re-evaluated for critical operations.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata:
        del metadata[evicted_key]
    
    for key in cache_snapshot.cache:
        metadata[key]['semigelatinous_score'] += SEMIGELATINOUS_ADJUSTMENT
        # Re-evaluate Kickapoo flag if necessary
        # Assuming a function `is_critical_operation` to determine criticality
        # metadata[key]['kickapoo'] = is_critical_operation(key)