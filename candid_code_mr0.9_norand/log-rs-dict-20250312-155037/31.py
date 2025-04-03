# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
DEFAULT_MOTORIZATION_RATE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including Farad (frequency of access), Unslinking (time since last access), Micromesentery (size of the object), and Motorization (rate of access change).
metadata = {}

def calculate_composite_score(farad, unslinking, micromesentery, motorization):
    # Composite score calculation (example formula, can be adjusted)
    return farad + unslinking + micromesentery + motorization

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score using Farad, Unslinking, Micromesentery, and Motorization. The object with the lowest score is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    lowest_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        farad = metadata[key]['farad']
        unslinking = cache_snapshot.access_count - metadata[key]['last_access_time']
        micromesentery = metadata[key]['micromesentery']
        motorization = metadata[key]['motorization']
        
        score = calculate_composite_score(farad, unslinking, micromesentery, motorization)
        
        if score < lowest_score:
            lowest_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, Farad is incremented, Unslinking is reset to zero, Micromesentery remains unchanged, and Motorization is updated based on the change in access frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata[key]['farad'] += 1
    metadata[key]['last_access_time'] = cache_snapshot.access_count
    metadata[key]['motorization'] = (metadata[key]['farad'] / (cache_snapshot.access_count - metadata[key]['initial_access_time']))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, Farad is initialized to one, Unslinking is set to zero, Micromesentery is recorded based on the object's size, and Motorization is initialized to a default rate.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata[key] = {
        'farad': 1,
        'last_access_time': cache_snapshot.access_count,
        'initial_access_time': cache_snapshot.access_count,
        'micromesentery': obj.size,
        'motorization': DEFAULT_MOTORIZATION_RATE
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting the victim, the metadata of the evicted object is removed from the cache, and the remaining objects' metadata are recalculated to ensure accurate composite scoring.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata:
        del metadata[evicted_key]
    
    for key in cache_snapshot.cache.keys():
        metadata[key]['motorization'] = (metadata[key]['farad'] / (cache_snapshot.access_count - metadata[key]['initial_access_time']))