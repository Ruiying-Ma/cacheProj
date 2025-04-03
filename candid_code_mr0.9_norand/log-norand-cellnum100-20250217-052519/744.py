# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQUENCY = 0.25
WEIGHT_LAST_ACCESS_TIMESTAMP = 0.25
WEIGHT_DATA_SYNTHESIS_SCORE = 0.25
WEIGHT_CONTEXTUAL_RELEVANCE_SCORE = 0.25

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, data synthesis score, and contextual relevance score for each cache entry.
metadata = {
    'access_frequency': {},
    'last_access_timestamp': {},
    'data_synthesis_score': {},
    'contextual_relevance_score': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a weighted score combining low access frequency, old last access timestamp, low data synthesis score, and low contextual relevance score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (
            WEIGHT_ACCESS_FREQUENCY * metadata['access_frequency'][key] +
            WEIGHT_LAST_ACCESS_TIMESTAMP * (cache_snapshot.access_count - metadata['last_access_timestamp'][key]) +
            WEIGHT_DATA_SYNTHESIS_SCORE * metadata['data_synthesis_score'][key] +
            WEIGHT_CONTEXTUAL_RELEVANCE_SCORE * metadata['contextual_relevance_score'][key]
        )
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency by incrementing it, refreshes the last access timestamp to the current time, recalculates the data synthesis score based on recent access patterns, and updates the contextual relevance score based on the current context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['last_access_timestamp'][key] = cache_snapshot.access_count
    metadata['data_synthesis_score'][key] = calculate_data_synthesis_score(obj)
    metadata['contextual_relevance_score'][key] = calculate_contextual_relevance_score(obj)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access timestamp to the current time, calculates an initial data synthesis score based on the object's characteristics, and assigns a contextual relevance score based on the current context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_timestamp'][key] = cache_snapshot.access_count
    metadata['data_synthesis_score'][key] = calculate_data_synthesis_score(obj)
    metadata['contextual_relevance_score'][key] = calculate_contextual_relevance_score(obj)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes all associated metadata for the evicted entry and recalibrates the data synthesis and contextual relevance scores for the remaining entries to ensure balanced cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del metadata['access_frequency'][evicted_key]
    del metadata['last_access_timestamp'][evicted_key]
    del metadata['data_synthesis_score'][evicted_key]
    del metadata['contextual_relevance_score'][evicted_key]
    
    for key in cache_snapshot.cache:
        metadata['data_synthesis_score'][key] = calculate_data_synthesis_score(cache_snapshot.cache[key])
        metadata['contextual_relevance_score'][key] = calculate_contextual_relevance_score(cache_snapshot.cache[key])

def calculate_data_synthesis_score(obj):
    '''
    Placeholder function to calculate the data synthesis score based on the object's characteristics.
    - Args:
        - `obj`: The object for which to calculate the score.
    - Return:
        - `score`: The calculated data synthesis score.
    '''
    # Implement the actual logic based on the object's characteristics
    return 1  # Placeholder value

def calculate_contextual_relevance_score(obj):
    '''
    Placeholder function to calculate the contextual relevance score based on the current context.
    - Args:
        - `obj`: The object for which to calculate the score.
    - Return:
        - `score`: The calculated contextual relevance score.
    '''
    # Implement the actual logic based on the current context
    return 1  # Placeholder value