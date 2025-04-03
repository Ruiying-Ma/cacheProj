# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
DEFAULT_ACCESS_PROBABILITY = 0.1
DEFAULT_TEMPORAL_DRIFT = 0
DEFAULT_PREDICTIVE_BUFFER_PRIORITY = 0
DEFAULT_ALGORITHMIC_LATENCY = 0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access probabilities, temporal drift scores, predictive buffer states, and algorithmic latency metrics for each cache entry.
metadata = {
    'access_probabilities': {},
    'temporal_drifts': {},
    'predictive_buffer_priorities': {},
    'algorithmic_latencies': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each entry, combining low access probability, high temporal drift misalignment, low predictive buffer priority, and high algorithmic latency. The entry with the highest composite score is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_composite_score = -float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_prob = metadata['access_probabilities'].get(key, DEFAULT_ACCESS_PROBABILITY)
        temporal_drift = metadata['temporal_drifts'].get(key, DEFAULT_TEMPORAL_DRIFT)
        predictive_buffer_priority = metadata['predictive_buffer_priorities'].get(key, DEFAULT_PREDICTIVE_BUFFER_PRIORITY)
        algorithmic_latency = metadata['algorithmic_latencies'].get(key, DEFAULT_ALGORITHMIC_LATENCY)
        
        composite_score = (1 - access_prob) + temporal_drift + (1 - predictive_buffer_priority) + algorithmic_latency
        
        if composite_score > max_composite_score:
            max_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access probability by incrementing it, recalculates the temporal drift score to align with the current access pattern, adjusts the predictive buffer state to reflect the recent access, and fine-tunes the algorithmic latency metric to optimize future access speed.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_probabilities'][key] = metadata['access_probabilities'].get(key, DEFAULT_ACCESS_PROBABILITY) + 1
    metadata['temporal_drifts'][key] = cache_snapshot.access_count
    metadata['predictive_buffer_priorities'][key] = 1
    metadata['algorithmic_latencies'][key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access probability to a default low value, sets the temporal drift score based on the current time, assigns a predictive buffer state indicating a new entry, and sets an initial algorithmic latency metric based on the insertion time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_probabilities'][key] = DEFAULT_ACCESS_PROBABILITY
    metadata['temporal_drifts'][key] = cache_snapshot.access_count
    metadata['predictive_buffer_priorities'][key] = 0
    metadata['algorithmic_latencies'][key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalibrates the access probabilities of remaining entries, adjusts their temporal drift scores to reflect the removal, updates the predictive buffer states to account for the freed space, and recalculates the algorithmic latency metrics to ensure optimal performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['access_probabilities']:
        del metadata['access_probabilities'][evicted_key]
    if evicted_key in metadata['temporal_drifts']:
        del metadata['temporal_drifts'][evicted_key]
    if evicted_key in metadata['predictive_buffer_priorities']:
        del metadata['predictive_buffer_priorities'][evicted_key]
    if evicted_key in metadata['algorithmic_latencies']:
        del metadata['algorithmic_latencies'][evicted_key]
    
    for key in cache_snapshot.cache:
        metadata['access_probabilities'][key] = max(metadata['access_probabilities'].get(key, DEFAULT_ACCESS_PROBABILITY) - 0.1, 0)
        metadata['temporal_drifts'][key] = cache_snapshot.access_count - metadata['temporal_drifts'].get(key, cache_snapshot.access_count)
        metadata['predictive_buffer_priorities'][key] = max(metadata['predictive_buffer_priorities'].get(key, DEFAULT_PREDICTIVE_BUFFER_PRIORITY) - 0.1, 0)
        metadata['algorithmic_latencies'][key] = cache_snapshot.access_count - metadata['algorithmic_latencies'].get(key, cache_snapshot.access_count)