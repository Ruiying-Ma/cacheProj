# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQUENCY = 1.0
WEIGHT_NEXT_ACCESS_TIME = 1.0
WEIGHT_MEMORY_USAGE = 1.0
WEIGHT_LATENCY_IMPACT = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted next access time, and memory usage footprint for each cached object.
metadata = {
    'access_frequency': {},
    'last_access_time': {},
    'predicted_next_access_time': {},
    'memory_usage_footprint': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a weighted score combining low access frequency, distant predicted next access time, high memory usage, and high latency impact.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_frequency = metadata['access_frequency'].get(key, 0)
        predicted_next_access_time = metadata['predicted_next_access_time'].get(key, float('inf'))
        memory_usage = cached_obj.size
        latency_impact = cache_snapshot.access_count - metadata['last_access_time'].get(key, 0)
        
        score = (WEIGHT_ACCESS_FREQUENCY / (access_frequency + 1)) + \
                (WEIGHT_NEXT_ACCESS_TIME * predicted_next_access_time) + \
                (WEIGHT_MEMORY_USAGE * memory_usage) + \
                (WEIGHT_LATENCY_IMPACT * latency_impact)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency by incrementing it, refreshes the last access time to the current time, and recalculates the predicted next access time using a predictive algorithm.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predicted_next_access_time'][key] = cache_snapshot.access_count + 2 * (cache_snapshot.access_count - metadata['last_access_time'].get(key, 0))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access time to the current time, predicts the next access time based on initial patterns, and records the memory usage footprint.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predicted_next_access_time'][key] = cache_snapshot.access_count + 10  # Initial prediction
    metadata['memory_usage_footprint'][key] = obj.size

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes all associated metadata for the evicted object and adjusts the dynamic resource allocation to optimize memory usage and reduce latency for remaining objects.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    if key in metadata['access_frequency']:
        del metadata['access_frequency'][key]
    if key in metadata['last_access_time']:
        del metadata['last_access_time'][key]
    if key in metadata['predicted_next_access_time']:
        del metadata['predicted_next_access_time'][key]
    if key in metadata['memory_usage_footprint']:
        del metadata['memory_usage_footprint'][key]