# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
INITIAL_PROB_THRESHOLD = 0.5
INITIAL_TEMPORAL_SPAN = 100
NORMALIZED_ACCESS_FREQ_DECAY = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains normalized access frequencies, predictive clusters of access patterns, probabilistic thresholds for eviction, and temporal spans of object lifetimes.
metadata = {
    'normalized_access_freq': {},  # key -> normalized access frequency
    'predictive_clusters': {},     # key -> cluster id
    'prob_thresholds': {},         # key -> probabilistic threshold
    'temporal_spans': {},          # key -> temporal span
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying objects with low normalized access frequencies within clusters that predict low future access, and those that fall below probabilistic thresholds within their temporal spans.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        norm_freq = metadata['normalized_access_freq'].get(key, 0)
        prob_threshold = metadata['prob_thresholds'].get(key, INITIAL_PROB_THRESHOLD)
        temporal_span = metadata['temporal_spans'].get(key, INITIAL_TEMPORAL_SPAN)
        
        score = norm_freq * prob_threshold / temporal_span
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the normalized access frequency of the object, adjusts its cluster membership based on recent access patterns, recalculates its probabilistic threshold, and extends its temporal span.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['normalized_access_freq'][key] = metadata['normalized_access_freq'].get(key, 0) * NORMALIZED_ACCESS_FREQ_DECAY + 1
    # Adjust cluster membership based on recent access patterns (simplified as keeping the same cluster)
    # Recalculate probabilistic threshold (simplified as keeping the same threshold)
    metadata['temporal_spans'][key] = cache_snapshot.access_count + INITIAL_TEMPORAL_SPAN

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its normalized access frequency, assigns it to a predictive cluster based on initial access patterns, sets an initial probabilistic threshold, and starts its temporal span.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['normalized_access_freq'][key] = 1
    metadata['predictive_clusters'][key] = 0  # Simplified as a single cluster
    metadata['prob_thresholds'][key] = INITIAL_PROB_THRESHOLD
    metadata['temporal_spans'][key] = cache_snapshot.access_count + INITIAL_TEMPORAL_SPAN

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting the victim, the policy removes its metadata, updates the predictive clusters to reflect the change, adjusts the probabilistic thresholds of remaining objects, and recalculates the temporal spans of the remaining objects.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['normalized_access_freq']:
        del metadata['normalized_access_freq'][evicted_key]
    if evicted_key in metadata['predictive_clusters']:
        del metadata['predictive_clusters'][evicted_key]
    if evicted_key in metadata['prob_thresholds']:
        del metadata['prob_thresholds'][evicted_key]
    if evicted_key in metadata['temporal_spans']:
        del metadata['temporal_spans'][evicted_key]
    
    # Adjust the probabilistic thresholds and temporal spans of remaining objects (simplified as keeping the same values)