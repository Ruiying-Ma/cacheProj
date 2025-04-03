# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
LFU_WEIGHT = 0.4
LRU_WEIGHT = 0.4
PATTERN_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency of access, and data stream patterns. It also tracks the performance metrics such as hit rate and latency to adaptively adjust its behavior.
metadata = {
    'access_frequency': {},  # key -> frequency
    'recency': {},           # key -> last access timestamp
    'data_stream_pattern': {},  # key -> pattern score
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a weighted score combining least frequently used (LFU), least recently used (LRU), and data stream pattern analysis. The object with the lowest score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        frequency = metadata['access_frequency'].get(key, 0)
        recency = metadata['recency'].get(key, 0)
        pattern = metadata['data_stream_pattern'].get(key, 0)
        
        score = (LFU_WEIGHT * frequency) + (LRU_WEIGHT * (cache_snapshot.access_count - recency)) + (PATTERN_WEIGHT * pattern)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the access frequency, updates the recency timestamp, and analyzes the data stream pattern to adjust the object's score. Performance metrics are also updated to reflect the hit.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['recency'][key] = cache_snapshot.access_count
    # Update data stream pattern if needed (this is a placeholder, actual pattern analysis logic can be complex)
    metadata['data_stream_pattern'][key] = metadata['data_stream_pattern'].get(key, 0) + 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency, sets the current timestamp as its recency, and begins tracking its data stream pattern. Performance metrics are updated to account for the insertion.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['data_stream_pattern'][key] = 1  # Initialize pattern score

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the metadata associated with the evicted object, recalculates the scores for remaining objects if necessary, and updates performance metrics to reflect the eviction event.
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
    if evicted_key in metadata['data_stream_pattern']:
        del metadata['data_stream_pattern'][evicted_key]