# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQ = 0.4
WEIGHT_RECENCY = 0.4
WEIGHT_PROB_SCORE = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, contextual tags (e.g., user behavior patterns), and a probabilistic score for each cache entry. It also keeps a dynamic scaling factor that adjusts based on cache performance metrics.
metadata = {
    'access_frequency': {},  # key -> access frequency
    'last_access_time': {},  # key -> last access time
    'probabilistic_score': {},  # key -> probabilistic score
    'contextual_tags': {},  # key -> contextual tags
    'dynamic_scaling_factor': 1.0  # dynamic scaling factor
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache entry, which is a weighted sum of the inverse of access frequency, recency, and the probabilistic score. The entry with the lowest composite score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_freq = metadata['access_frequency'].get(key, 1)
        last_access = metadata['last_access_time'].get(key, 0)
        prob_score = metadata['probabilistic_score'].get(key, 1.0)
        
        inverse_access_freq = 1 / access_freq
        recency = cache_snapshot.access_count - last_access
        
        composite_score = (WEIGHT_ACCESS_FREQ * inverse_access_freq +
                           WEIGHT_RECENCY * recency +
                           WEIGHT_PROB_SCORE * prob_score)
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency is incremented, the last access time is updated to the current time, and the probabilistic score is adjusted based on the contextual tags and dynamic scaling factor. Recursive feedback is used to refine the probabilistic mapping.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    # Adjust probabilistic score based on contextual tags and dynamic scaling factor
    metadata['probabilistic_score'][key] = metadata['contextual_tags'].get(key, 1.0) * metadata['dynamic_scaling_factor']

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency to 1, sets the last access time to the current time, assigns initial contextual tags, and calculates an initial probabilistic score. The dynamic scaling factor is adjusted based on the current cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['contextual_tags'][key] = 1.0  # Initial contextual tag
    metadata['probabilistic_score'][key] = 1.0 * metadata['dynamic_scaling_factor']
    # Adjust dynamic scaling factor based on current cache performance
    metadata['dynamic_scaling_factor'] = (cache_snapshot.hit_count + 1) / (cache_snapshot.miss_count + 1)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalculates the dynamic scaling factor to reflect the change in cache composition and performance. It also updates the probabilistic mapping using recursive feedback from the eviction decision to improve future eviction choices.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Remove metadata for evicted object
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['last_access_time']:
        del metadata['last_access_time'][evicted_key]
    if evicted_key in metadata['probabilistic_score']:
        del metadata['probabilistic_score'][evicted_key]
    if evicted_key in metadata['contextual_tags']:
        del metadata['contextual_tags'][evicted_key]
    
    # Recalculate dynamic scaling factor
    metadata['dynamic_scaling_factor'] = (cache_snapshot.hit_count + 1) / (cache_snapshot.miss_count + 1)
    # Update probabilistic mapping using recursive feedback
    for key in metadata['probabilistic_score']:
        metadata['probabilistic_score'][key] *= metadata['dynamic_scaling_factor']