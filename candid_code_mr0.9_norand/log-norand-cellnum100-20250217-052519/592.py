# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQUENCY = 0.4
WEIGHT_RECENCY = 0.3
WEIGHT_PREDICTED_FUTURE_ACCESS = 0.2
WEIGHT_TEMPORAL_PATTERN_SCORE = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted future access time, and a temporal pattern score for each cached object. It also keeps a global adaptive buffer size based on recent cache hit/miss ratios.
metadata = {
    'access_frequency': {},
    'last_access_time': {},
    'predicted_future_access_time': {},
    'temporal_pattern_score': {},
    'global_adaptive_buffer_size': 0,
    'last_hit_count': 0,
    'last_miss_count': 0
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each object, which is a weighted sum of its access frequency, recency, predicted future access time, and temporal pattern score. The object with the lowest composite score is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_frequency = metadata['access_frequency'].get(key, 0)
        last_access_time = metadata['last_access_time'].get(key, 0)
        predicted_future_access_time = metadata['predicted_future_access_time'].get(key, float('inf'))
        temporal_pattern_score = metadata['temporal_pattern_score'].get(key, 0)
        
        composite_score = (
            WEIGHT_ACCESS_FREQUENCY * access_frequency +
            WEIGHT_RECENCY * (cache_snapshot.access_count - last_access_time) +
            WEIGHT_PREDICTED_FUTURE_ACCESS * predicted_future_access_time +
            WEIGHT_TEMPORAL_PATTERN_SCORE * temporal_pattern_score
        )
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the access frequency and last access time of the object are updated. The temporal pattern score is recalculated based on recent access patterns. The global adaptive buffer size is adjusted if the hit/miss ratio has changed significantly.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    
    # Recalculate temporal pattern score (simplified for this example)
    metadata['temporal_pattern_score'][key] = metadata['access_frequency'][key] / (cache_snapshot.access_count - metadata['last_access_time'][key] + 1)
    
    # Adjust global adaptive buffer size if hit/miss ratio has changed significantly
    current_hit_count = cache_snapshot.hit_count
    current_miss_count = cache_snapshot.miss_count
    if current_hit_count + current_miss_count > 0:
        current_hit_ratio = current_hit_count / (current_hit_count + current_miss_count)
        last_hit_ratio = metadata['last_hit_count'] / (metadata['last_hit_count'] + metadata['last_miss_count']) if (metadata['last_hit_count'] + metadata['last_miss_count']) > 0 else 0
        if abs(current_hit_ratio - last_hit_ratio) > 0.1:  # Threshold for significant change
            metadata['global_adaptive_buffer_size'] = int(cache_snapshot.capacity * current_hit_ratio)
    
    metadata['last_hit_count'] = current_hit_count
    metadata['last_miss_count'] = current_miss_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its initial metadata values are set, including a default access frequency, current time as the last access time, an initial predicted future access time, and a temporal pattern score based on initial access patterns. The global adaptive buffer size is also recalibrated if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predicted_future_access_time'][key] = cache_snapshot.access_count + 100  # Simplified prediction
    metadata['temporal_pattern_score'][key] = 1  # Initial score
    
    # Recalibrate global adaptive buffer size if necessary
    current_hit_count = cache_snapshot.hit_count
    current_miss_count = cache_snapshot.miss_count
    if current_hit_count + current_miss_count > 0:
        current_hit_ratio = current_hit_count / (current_hit_count + current_miss_count)
        metadata['global_adaptive_buffer_size'] = int(cache_snapshot.capacity * current_hit_ratio)
    
    metadata['last_hit_count'] = current_hit_count
    metadata['last_miss_count'] = current_miss_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy recalculates the global adaptive buffer size based on the new cache state. It also updates the temporal pattern recognition model to improve future predictions and adjusts the weights used in the composite score calculation if needed.
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
    if evicted_key in metadata['temporal_pattern_score']:
        del metadata['temporal_pattern_score'][evicted_key]
    
    # Recalculate global adaptive buffer size
    current_hit_count = cache_snapshot.hit_count
    current_miss_count = cache_snapshot.miss_count
    if current_hit_count + current_miss_count > 0:
        current_hit_ratio = current_hit_count / (current_hit_count + current_miss_count)
        metadata['global_adaptive_buffer_size'] = int(cache_snapshot.capacity * current_hit_ratio)
    
    metadata['last_hit_count'] = current_hit_count
    metadata['last_miss_count'] = current_miss_count