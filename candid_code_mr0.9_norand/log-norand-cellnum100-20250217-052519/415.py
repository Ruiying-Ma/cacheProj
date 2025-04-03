# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQUENCY = 1.0
WEIGHT_LAST_ACCESS_TIME = 1.0
WEIGHT_PREDICTED_FUTURE_ACCESS_TIME = 1.0
WEIGHT_RESOURCE_USAGE = 1.0
WEIGHT_NETWORK_LATENCY = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted future access time, resource usage, and network latency for each cached object.
metadata = {
    'access_frequency': {},
    'last_access_time': {},
    'predicted_future_access_time': {},
    'resource_usage': {},
    'network_latency': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a weighted score that considers low access frequency, longest time since last access, longest predicted future access time, high resource usage, and high network latency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (
            WEIGHT_ACCESS_FREQUENCY * metadata['access_frequency'][key] +
            WEIGHT_LAST_ACCESS_TIME * (cache_snapshot.access_count - metadata['last_access_time'][key]) +
            WEIGHT_PREDICTED_FUTURE_ACCESS_TIME * metadata['predicted_future_access_time'][key] +
            WEIGHT_RESOURCE_USAGE * metadata['resource_usage'][key] +
            WEIGHT_NETWORK_LATENCY * metadata['network_latency'][key]
        )
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency by incrementing it, sets the last access time to the current time, adjusts the predicted future access time based on recent patterns, and recalculates resource usage and network latency if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    # Adjust predicted future access time, resource usage, and network latency if necessary
    # For simplicity, we assume they remain constant in this example

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access time to the current time, estimates the predicted future access time based on initial patterns, and records the initial resource usage and network latency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predicted_future_access_time'][key] = 1  # Initial pattern
    metadata['resource_usage'][key] = obj.size  # Assuming resource usage is proportional to size
    metadata['network_latency'][key] = 1  # Initial network latency

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes all metadata associated with the evicted object and recalculates the overall resource allocation and network optimization metrics to ensure fault tolerance and efficient resource usage.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del metadata['access_frequency'][evicted_key]
    del metadata['last_access_time'][evicted_key]
    del metadata['predicted_future_access_time'][evicted_key]
    del metadata['resource_usage'][evicted_key]
    del metadata['network_latency'][evicted_key]
    # Recalculate overall resource allocation and network optimization metrics if necessary