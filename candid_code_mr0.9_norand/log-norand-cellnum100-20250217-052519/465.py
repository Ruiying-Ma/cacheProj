# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
PREDICTIVE_SCORE_DECAY = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, context tags (e.g., user, application), and a predictive score based on historical access patterns. It also tracks load distribution across different cache segments.
metadata = {
    'access_frequency': {},
    'last_access_time': {},
    'context_tags': {},
    'predictive_score': {},
    'load_distribution': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by combining context-aware analysis and predictive eviction scores. It prioritizes evicting items with low predictive scores and low access frequency, while also considering temporal coherence to avoid evicting recently accessed items.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (metadata['predictive_score'][key] * PREDICTIVE_SCORE_DECAY) / (metadata['access_frequency'][key] + 1)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency, refreshes the last access time, and recalculates the predictive score based on the new access pattern. It also adjusts the load distribution metadata to reflect the current state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predictive_score'][key] = metadata['access_frequency'][key] / (cache_snapshot.access_count - metadata['last_access_time'][key] + 1)
    # Adjust load distribution if necessary

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency, sets the current time as the last access time, assigns context tags, and calculates an initial predictive score. It updates the load distribution to account for the new object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['context_tags'][key] = 'default'  # Assign context tags as needed
    metadata['predictive_score'][key] = 1 / (cache_snapshot.access_count + 1)
    # Update load distribution

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the metadata associated with the evicted object, recalculates the load distribution, and adjusts the predictive scores of remaining objects to reflect the change in cache composition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del metadata['access_frequency'][evicted_key]
    del metadata['last_access_time'][evicted_key]
    del metadata['context_tags'][evicted_key]
    del metadata['predictive_score'][evicted_key]
    # Recalculate load distribution