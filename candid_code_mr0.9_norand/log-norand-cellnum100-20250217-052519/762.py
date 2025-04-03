# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
INITIAL_THRESHOLD = 10

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted future access time, and a dynamic threshold value for each cache entry. It also keeps a global statistical model to predict future access patterns.
metadata = {
    'access_frequency': {},  # key -> frequency
    'last_access_time': {},  # key -> last access time
    'predicted_future_access_time': {},  # key -> predicted future access time
    'dynamic_threshold': INITIAL_THRESHOLD  # dynamic threshold value
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by comparing the predicted future access times of all cache entries against a dynamically tuned threshold. Entries with predicted access times beyond this threshold are considered for eviction, prioritizing those with the lowest access frequency and longest time since last access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_frequency = float('inf')
    max_last_access_time = -1

    for key, cached_obj in cache_snapshot.cache.items():
        predicted_time = metadata['predicted_future_access_time'].get(key, float('inf'))
        if predicted_time > metadata['dynamic_threshold']:
            frequency = metadata['access_frequency'].get(key, 0)
            last_access_time = metadata['last_access_time'].get(key, 0)
            if (frequency < min_frequency) or (frequency == min_frequency and last_access_time > max_last_access_time):
                min_frequency = frequency
                max_last_access_time = last_access_time
                candid_obj_key = key

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency and last access time of the hit entry. It also refines the global statistical model using real-time monitoring data to improve future access predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    # Update the global statistical model (simplified as updating predicted future access time)
    metadata['predicted_future_access_time'][key] = cache_snapshot.access_count + metadata['dynamic_threshold']

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency and last access time. It also updates the global statistical model to incorporate the new entry, adjusting the dynamic threshold based on current cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predicted_future_access_time'][key] = cache_snapshot.access_count + metadata['dynamic_threshold']
    # Adjust the dynamic threshold based on current cache performance (simplified)
    if cache_snapshot.miss_count > cache_snapshot.hit_count:
        metadata['dynamic_threshold'] += 1
    else:
        metadata['dynamic_threshold'] = max(1, metadata['dynamic_threshold'] - 1)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the metadata of the evicted entry and recalibrates the global statistical model. It also adjusts the dynamic threshold to reflect the current cache state and access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['last_access_time']:
        del metadata['last_access_time'][evicted_key]
    if evicted_key in metadata['predicted_future_access_time']:
        del metadata['predicted_future_access_time'][evicted_key]
    # Recalibrate the global statistical model (simplified)
    if cache_snapshot.miss_count > cache_snapshot.hit_count:
        metadata['dynamic_threshold'] += 1
    else:
        metadata['dynamic_threshold'] = max(1, metadata['dynamic_threshold'] - 1)