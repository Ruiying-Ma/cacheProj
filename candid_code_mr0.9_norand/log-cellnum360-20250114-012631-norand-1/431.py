# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
INITIAL_VARIANCE_SCORE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, contextual information (e.g., time of day, user behavior patterns), and a stochastic variance score that measures the unpredictability of access patterns.
metadata = {
    'access_frequency': {},  # key -> frequency
    'last_access_time': {},  # key -> last access time
    'contextual_info': {},   # key -> contextual information
    'variance_score': {}     # key -> variance score
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by combining predictive optimization (forecasting future accesses based on historical data), contextual recalibration (adjusting predictions based on current context), and stochastic variance (preferring to evict items with higher unpredictability scores).
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        # Calculate a combined score for eviction
        frequency = metadata['access_frequency'].get(key, 0)
        last_access = metadata['last_access_time'].get(key, 0)
        variance = metadata['variance_score'].get(key, INITIAL_VARIANCE_SCORE)
        
        # Example combined score: lower frequency, older access time, higher variance
        score = (1 / (frequency + 1)) + (cache_snapshot.access_count - last_access) + variance
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency, last access time, and recalibrates the contextual information. It also adjusts the stochastic variance score to reflect the reduced uncertainty of the accessed item.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    # Recalibrate contextual information (example: time of day)
    metadata['contextual_info'][key] = cache_snapshot.access_count % 24  # Example: hour of the day
    # Adjust variance score
    metadata['variance_score'][key] = max(0, metadata['variance_score'].get(key, INITIAL_VARIANCE_SCORE) - 0.1)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency, sets the last access time to the current time, captures the current contextual information, and assigns an initial stochastic variance score based on the object's predicted access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['contextual_info'][key] = cache_snapshot.access_count % 24  # Example: hour of the day
    metadata['variance_score'][key] = INITIAL_VARIANCE_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalibrates the contextual information to reflect the change in the cache state and updates the stochastic variance scores of remaining items to account for the removal of the evicted item.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Remove metadata of the evicted object
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['last_access_time']:
        del metadata['last_access_time'][evicted_key]
    if evicted_key in metadata['contextual_info']:
        del metadata['contextual_info'][evicted_key]
    if evicted_key in metadata['variance_score']:
        del metadata['variance_score'][evicted_key]
    
    # Recalibrate contextual information and variance scores for remaining items
    for key in cache_snapshot.cache:
        metadata['contextual_info'][key] = cache_snapshot.access_count % 24  # Example: hour of the day
        metadata['variance_score'][key] = min(INITIAL_VARIANCE_SCORE, metadata['variance_score'].get(key, INITIAL_VARIANCE_SCORE) + 0.1)