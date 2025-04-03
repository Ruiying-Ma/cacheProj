# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
w1 = 1
w2 = 1
w3 = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a metadata structure consisting of access_counter, frequency_diversity, and recent_update_time for each object in the cache.
metadata = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on the object with the lowest value derived from a weighted formula: w1*access_counter + w2*frequency_diversity - w3*recent_update_time, where w1, w2, and w3 are pre-defined weights.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_value = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_counter = metadata[key]['access_counter']
        frequency_diversity = metadata[key]['frequency_diversity']
        recent_update_time = metadata[key]['recent_update_time']
        
        value = w1 * access_counter + w2 * frequency_diversity - w3 * recent_update_time
        
        if value < min_value:
            min_value = value
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    On a cache hit, the policy increments the access_counter for the hit object, recalculates its frequency_diversity by factoring in the new reference, and updates the recent_update_time to the current timestamp.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata[key]['access_counter'] += 1
    metadata[key]['frequency_diversity'] += 1  # Assuming frequency_diversity is incremented by 1 for each hit
    metadata[key]['recent_update_time'] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    Upon inserting a new object, the policy initializes access_counter to 1, calculates the initial frequency_diversity based on object type/category or other characteristics, and sets recent_update_time to the current timestamp.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata[key] = {
        'access_counter': 1,
        'frequency_diversity': 1,  # Assuming initial frequency_diversity is 1
        'recent_update_time': cache_snapshot.access_count
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy cleans up by removing all the associated metadata for the victim from the metadata structure to ensure no residual information affects future decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    if key in metadata:
        del metadata[key]