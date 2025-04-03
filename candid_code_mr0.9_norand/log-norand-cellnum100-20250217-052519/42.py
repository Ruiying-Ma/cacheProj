# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
INITIAL_PREDICTIVE_SCORE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, and a predictive score for each cache entry. It also tracks global access patterns to adaptively adjust the predictive heuristic.
metadata = {
    'access_frequency': {},  # key -> access frequency
    'last_access_time': {},  # key -> last access time
    'predictive_score': {},  # key -> predictive score
    'global_access_pattern': 0  # a heuristic value to adjust predictive scores
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a combined score derived from the inverse of access frequency, recency of access, and the predictive score. The entry with the lowest combined score is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_freq = metadata['access_frequency'].get(key, 1)
        last_access = metadata['last_access_time'].get(key, 0)
        predictive_score = metadata['predictive_score'].get(key, INITIAL_PREDICTIVE_SCORE)
        
        combined_score = (1 / access_freq) + (cache_snapshot.access_count - last_access) + predictive_score
        
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency is incremented, the last access time is updated to the current time, and the predictive score is adjusted based on recent global access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predictive_score'][key] = metadata['global_access_pattern']

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency to 1, sets the last access time to the current time, and assigns an initial predictive score based on global access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predictive_score'][key] = metadata['global_access_pattern']

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy recalculates global access patterns and adjusts the predictive heuristic to improve future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Recalculate global access patterns
    total_accesses = sum(metadata['access_frequency'].values())
    if total_accesses > 0:
        metadata['global_access_pattern'] = total_accesses / len(metadata['access_frequency'])
    else:
        metadata['global_access_pattern'] = INITIAL_PREDICTIVE_SCORE