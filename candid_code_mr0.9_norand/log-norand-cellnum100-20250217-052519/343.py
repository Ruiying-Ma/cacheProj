# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for access frequency in composite score
BETA = 0.3   # Weight for last access time in composite score
GAMMA = 0.1  # Weight for predicted future access time in composite score
DELTA = 0.1  # Weight for data locality score in composite score

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted future access time, and data locality score for each cached object. It also keeps track of the overall workload pattern and latency metrics.
metadata = {
    'access_frequency': {},  # {obj.key: frequency}
    'last_access_time': {},  # {obj.key: last_access_time}
    'predicted_future_access_time': {},  # {obj.key: predicted_future_access_time}
    'data_locality_score': {},  # {obj.key: data_locality_score}
    'workload_pattern': {},  # {obj.key: workload_pattern}
    'latency_metrics': {}  # {obj.key: latency_metrics}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a composite score derived from the object's access frequency, last access time, predicted future access time, and data locality score. Objects with the lowest composite score are evicted first.
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
        last_access_time = metadata['last_access_time'].get(key, 0)
        predicted_future_access_time = metadata['predicted_future_access_time'].get(key, float('inf'))
        data_locality_score = metadata['data_locality_score'].get(key, 0)
        
        composite_score = (ALPHA * access_frequency +
                           BETA * last_access_time +
                           GAMMA * predicted_future_access_time +
                           DELTA * data_locality_score)
        
        if composite_score < min_score:
            min_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency, last access time, and recalculates the predicted future access time for the object. The data locality score is adjusted based on the current workload pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Update access frequency
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    
    # Update last access time
    metadata['last_access_time'][key] = current_time
    
    # Recalculate predicted future access time (simple heuristic: next access in twice the time since last access)
    last_access_time = metadata['last_access_time'][key]
    metadata['predicted_future_access_time'][key] = current_time + (current_time - last_access_time)
    
    # Adjust data locality score based on current workload pattern
    metadata['data_locality_score'][key] = metadata['data_locality_score'].get(key, 0) + 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency, sets the last access time to the current time, predicts the future access time based on workload patterns, and calculates an initial data locality score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Initialize access frequency
    metadata['access_frequency'][key] = 1
    
    # Set last access time to current time
    metadata['last_access_time'][key] = current_time
    
    # Predict future access time (simple heuristic: next access in twice the current time)
    metadata['predicted_future_access_time'][key] = current_time * 2
    
    # Calculate initial data locality score
    metadata['data_locality_score'][key] = 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy updates the overall workload pattern and latency metrics to reflect the change. It also recalibrates the data locality scores of remaining objects if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove metadata of evicted object
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['last_access_time']:
        del metadata['last_access_time'][evicted_key]
    if evicted_key in metadata['predicted_future_access_time']:
        del metadata['predicted_future_access_time'][evicted_key]
    if evicted_key in metadata['data_locality_score']:
        del metadata['data_locality_score'][evicted_key]
    
    # Update workload pattern and latency metrics
    # (This is a placeholder, as the actual implementation would depend on specific workload and latency metrics)
    metadata['workload_pattern'][evicted_key] = metadata['workload_pattern'].get(evicted_key, 0) + 1
    metadata['latency_metrics'][evicted_key] = metadata['latency_metrics'].get(evicted_key, 0) + 1
    
    # Recalibrate data locality scores if necessary
    for key in cache_snapshot.cache:
        metadata['data_locality_score'][key] = metadata['data_locality_score'].get(key, 0) + 1