# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
AGE_WEIGHT = 1.0
FREQUENCY_WEIGHT = 1.0
PREDICTED_FUTURE_ACCESS_WEIGHT = 1.0
LATENCY_SENSITIVITY_WEIGHT = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access timestamps, access frequency, predicted future access time, and latency sensitivity for each cached object.
metadata = {
    'access_timestamps': {},  # {obj.key: timestamp}
    'access_frequencies': {},  # {obj.key: frequency}
    'predicted_future_access_times': {},  # {obj.key: predicted_future_access_time}
    'latency_sensitivities': {}  # {obj.key: latency_sensitivity}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a score for each object based on a weighted combination of its age, access frequency, predicted future access time, and latency sensitivity. The object with the lowest score is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        age = cache_snapshot.access_count - metadata['access_timestamps'][key]
        frequency = metadata['access_frequencies'][key]
        predicted_future_access_time = metadata['predicted_future_access_times'][key]
        latency_sensitivity = metadata['latency_sensitivities'][key]
        
        score = (AGE_WEIGHT * age) - (FREQUENCY_WEIGHT * frequency) + \
                (PREDICTED_FUTURE_ACCESS_WEIGHT * predicted_future_access_time) + \
                (LATENCY_SENSITIVITY_WEIGHT * latency_sensitivity)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access timestamp to the current time, increments the access frequency, and refines the predicted future access time based on recent access patterns. Latency sensitivity is adjusted if the access latency deviates significantly from the expected value.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    metadata['access_timestamps'][obj.key] = current_time
    metadata['access_frequencies'][obj.key] += 1
    # Refine predicted future access time (simple heuristic)
    metadata['predicted_future_access_times'][obj.key] = current_time + 10
    # Adjust latency sensitivity (simple heuristic)
    metadata['latency_sensitivities'][obj.key] = max(1, metadata['latency_sensitivities'][obj.key] - 1)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access timestamp to the current time, sets the access frequency to one, estimates the predicted future access time based on similar objects, and assigns an initial latency sensitivity based on the object's type and historical data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    metadata['access_timestamps'][obj.key] = current_time
    metadata['access_frequencies'][obj.key] = 1
    # Estimate predicted future access time (simple heuristic)
    metadata['predicted_future_access_times'][obj.key] = current_time + 20
    # Assign initial latency sensitivity (simple heuristic)
    metadata['latency_sensitivities'][obj.key] = 5

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy recalculates the predicted future access times and latency sensitivities for the remaining objects to ensure optimal scheduling and resource allocation.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Remove metadata for evicted object
    del metadata['access_timestamps'][evicted_obj.key]
    del metadata['access_frequencies'][evicted_obj.key]
    del metadata['predicted_future_access_times'][evicted_obj.key]
    del metadata['latency_sensitivities'][evicted_obj.key]
    
    # Recalculate predicted future access times and latency sensitivities for remaining objects (simple heuristic)
    for key in cache_snapshot.cache:
        metadata['predicted_future_access_times'][key] = cache_snapshot.access_count + 15
        metadata['latency_sensitivities'][key] = max(1, metadata['latency_sensitivities'][key] - 1)