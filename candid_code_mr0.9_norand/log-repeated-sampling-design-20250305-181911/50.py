# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 1.0
RECENCY_WEIGHT = 1.0
EVICTION_AGE_WEIGHT = 1.0

# Put the metadata specifically maintained by the policy below. This policy maintains metadata on the frequency of access ('frequency'), the recency of access ('recency'), and the time since last eviction ('eviction_age') for each cached object.
metadata = {
    'frequency': {},
    'recency': {},
    'eviction_age': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The victim for eviction is chosen based on a composite score that factors in low access frequency, high recency (older accesses get higher score), and high eviction_age. The object with the highest composite score is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_score = -float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        frequency = metadata['frequency'].get(key, 0)
        recency = metadata['recency'].get(key, 0)
        eviction_age = metadata['eviction_age'].get(key, 0)
        
        score = (FREQUENCY_WEIGHT * (1 / (frequency + 1)) +
                 RECENCY_WEIGHT * recency +
                 EVICTION_AGE_WEIGHT * eviction_age)
        
        if score > max_score:
            max_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, increase the 'frequency' and update the 'recency' to the current time for the accessed object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['frequency'][key] = metadata['frequency'].get(key, 0) + 1
    metadata['recency'][key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    Immediately after inserting a new object, set its 'frequency' to 1, 'recency' to the current time, and 'eviction_age' to 0.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['frequency'][key] = 1
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['eviction_age'][key] = 0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, increment the 'eviction_age' for all remaining objects in the cache that were accessed prior to the eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    evicted_recency = metadata['recency'].get(evicted_key, 0)
    
    for key in cache_snapshot.cache:
        if metadata['recency'].get(key, 0) < evicted_recency:
            metadata['eviction_age'][key] = metadata['eviction_age'].get(key, 0) + 1