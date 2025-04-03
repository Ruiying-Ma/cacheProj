# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
PROBABILISTIC_SCORE_BASE = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, contextual tags (e.g., user behavior patterns, application type), and a probabilistic score predicting future accesses.
metadata = {
    'access_frequency': {},
    'last_access_time': {},
    'contextual_tags': {},
    'probabilistic_score': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache entry, which combines the inverse of access frequency, recency of access, and the probabilistic score. The entry with the lowest composite score is evicted.
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
        prob_score = metadata['probabilistic_score'].get(key, PROBABILISTIC_SCORE_BASE)
        
        composite_score = (1 / access_freq) + (cache_snapshot.access_count - last_access) + prob_score
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency by incrementing it, refreshes the last access time to the current time, and recalculates the probabilistic score based on the updated access pattern and contextual tags.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    # Recalculate probabilistic score based on updated access pattern and contextual tags
    metadata['probabilistic_score'][key] = PROBABILISTIC_SCORE_BASE / metadata['access_frequency'][key]

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access time to the current time, assigns contextual tags based on the insertion context, and computes an initial probabilistic score for future accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['contextual_tags'][key] = 'default'  # Example tag, can be more complex
    metadata['probabilistic_score'][key] = PROBABILISTIC_SCORE_BASE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy adjusts the probabilistic model parameters to reflect the removal, updates contextual optimization parameters to improve future predictions, and recalibrates the overall cache state to maintain temporal coherence.
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
    if evicted_key in metadata['contextual_tags']:
        del metadata['contextual_tags'][evicted_key]
    if evicted_key in metadata['probabilistic_score']:
        del metadata['probabilistic_score'][evicted_key]
    
    # Adjust probabilistic model parameters and recalibrate cache state
    # This is a placeholder for more complex logic