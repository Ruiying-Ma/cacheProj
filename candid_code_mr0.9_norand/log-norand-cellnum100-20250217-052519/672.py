# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
INITIAL_PREDICTED_FUTURE_ACCESS_TIME = 1000  # Example constant for initial predicted future access time

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted future access time, and contextual information such as user behavior patterns and system load.
metadata = {
    'access_frequency': {},  # key -> access frequency
    'last_access_time': {},  # key -> last access time
    'predicted_future_access_time': {},  # key -> predicted future access time
    'contextual_info': {}  # key -> contextual information (e.g., user behavior patterns)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by combining real-time analytics and predictive modeling to identify the object with the lowest predicted future access probability, while also considering current system load and user context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_predicted_access_time = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        predicted_access_time = metadata['predicted_future_access_time'].get(key, float('inf'))
        if predicted_access_time < min_predicted_access_time:
            min_predicted_access_time = predicted_access_time
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency, last access time, and refines the predictive model based on the new access pattern, also adjusting the contextual information to reflect the current user behavior.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Update access frequency
    if key in metadata['access_frequency']:
        metadata['access_frequency'][key] += 1
    else:
        metadata['access_frequency'][key] = 1
    
    # Update last access time
    metadata['last_access_time'][key] = current_time
    
    # Refine predictive model (simple example: decrease predicted future access time)
    if key in metadata['predicted_future_access_time']:
        metadata['predicted_future_access_time'][key] -= 1
    
    # Adjust contextual information (example: update user behavior pattern)
    metadata['contextual_info'][key] = 'updated_behavior_pattern'

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its metadata with current access time, sets an initial predicted future access time based on similar objects, and updates the contextual information to include the new object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Initialize metadata
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = current_time
    metadata['predicted_future_access_time'][key] = INITIAL_PREDICTED_FUTURE_ACCESS_TIME
    metadata['contextual_info'][key] = 'initial_behavior_pattern'

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes its metadata, recalibrates the predictive model to account for the eviction, and adjusts the contextual information to reflect the change in the cache content.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove metadata
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['last_access_time']:
        del metadata['last_access_time'][evicted_key]
    if evicted_key in metadata['predicted_future_access_time']:
        del metadata['predicted_future_access_time'][evicted_key]
    if evicted_key in metadata['contextual_info']:
        del metadata['contextual_info'][evicted_key]
    
    # Recalibrate predictive model (example: adjust based on remaining objects)
    for key in metadata['predicted_future_access_time']:
        metadata['predicted_future_access_time'][key] += 1
    
    # Adjust contextual information (example: update system load)
    for key in metadata['contextual_info']:
        metadata['contextual_info'][key] = 'adjusted_behavior_pattern'