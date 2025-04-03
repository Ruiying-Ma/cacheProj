# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for access frequency
BETA = 0.3   # Weight for recency
GAMMA = 0.1  # Weight for data stream priority
DELTA = 0.1  # Weight for event-driven importance

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency of access, data stream priority, and event-driven importance scores for each cached object.
metadata = {
    'access_frequency': {},  # Dictionary to store access frequency of each object
    'recency': {},           # Dictionary to store recency timestamp of each object
    'data_stream_priority': {},  # Dictionary to store data stream priority of each object
    'importance_score': {}   # Dictionary to store event-driven importance score of each object
}

def calculate_composite_score(key):
    '''
    Helper function to calculate the composite score for an object based on its metadata.
    - Args:
        - `key`: The key of the object.
    - Return:
        - `score`: The composite score of the object.
    '''
    freq = metadata['access_frequency'].get(key, 0)
    recency = metadata['recency'].get(key, 0)
    priority = metadata['data_stream_priority'].get(key, 0)
    importance = metadata['importance_score'].get(key, 0)
    
    score = (ALPHA * freq) + (BETA * recency) + (GAMMA * priority) + (DELTA * importance)
    return score

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each object based on its access frequency, recency, data stream priority, and event-driven importance. The object with the lowest composite score is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key in cache_snapshot.cache:
        score = calculate_composite_score(key)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy increments the access frequency, updates the recency timestamp, and recalculates the event-driven importance score for the accessed object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['importance_score'][key] = calculate_composite_score(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency, sets the current timestamp as the recency, assigns a data stream priority based on the stream it belongs to, and calculates an initial event-driven importance score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['data_stream_priority'][key] = 1  # Assuming a default priority of 1 for simplicity
    metadata['importance_score'][key] = calculate_composite_score(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy removes all associated metadata for the evicted object and adjusts the event-driven importance scores of remaining objects if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['recency']:
        del metadata['recency'][evicted_key]
    if evicted_key in metadata['data_stream_priority']:
        del metadata['data_stream_priority'][evicted_key]
    if evicted_key in metadata['importance_score']:
        del metadata['importance_score'][evicted_key]
    
    # Adjust importance scores of remaining objects if necessary
    for key in cache_snapshot.cache:
        metadata['importance_score'][key] = calculate_composite_score(key)