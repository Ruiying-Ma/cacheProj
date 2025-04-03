# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
INITIAL_PREDICTIVE_UTILITY_SCORE = 1.0
INITIAL_ADAPTIVE_LATENCY_SCORE = 1.0
INITIAL_PROBABILISTIC_FAULT_TOLERANCE_SCORE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive utility score for each cache entry, an adaptive latency score, a probabilistic fault tolerance score, and context-aware usage patterns.
metadata = {
    'predictive_utility': {},  # key -> predictive utility score
    'adaptive_latency': {},    # key -> adaptive latency score
    'fault_tolerance': {},     # key -> probabilistic fault tolerance score
    'context_usage': {}        # key -> context-aware usage patterns
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score that combines the predictive utility score, adaptive latency score, and probabilistic fault tolerance score, while considering the current context-aware usage patterns. The entry with the lowest composite score is chosen for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        predictive_utility = metadata['predictive_utility'].get(key, INITIAL_PREDICTIVE_UTILITY_SCORE)
        adaptive_latency = metadata['adaptive_latency'].get(key, INITIAL_ADAPTIVE_LATENCY_SCORE)
        fault_tolerance = metadata['fault_tolerance'].get(key, INITIAL_PROBABILISTIC_FAULT_TOLERANCE_SCORE)
        context_usage = metadata['context_usage'].get(key, 1.0)
        
        composite_score = predictive_utility + adaptive_latency + fault_tolerance + context_usage
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the predictive utility score is increased based on the frequency and recency of access. The adaptive latency score is adjusted based on the observed access latency. The probabilistic fault tolerance score is updated to reflect the reliability of the entry. Context-aware usage patterns are refined to better predict future accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['predictive_utility'][key] = metadata['predictive_utility'].get(key, INITIAL_PREDICTIVE_UTILITY_SCORE) + 1
    metadata['adaptive_latency'][key] = metadata['adaptive_latency'].get(key, INITIAL_ADAPTIVE_LATENCY_SCORE) * 0.9
    metadata['fault_tolerance'][key] = metadata['fault_tolerance'].get(key, INITIAL_PROBABILISTIC_FAULT_TOLERANCE_SCORE) * 1.1
    metadata['context_usage'][key] = metadata['context_usage'].get(key, 1.0) * 1.05

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the predictive utility score is initialized based on initial access patterns. The adaptive latency score is set according to the initial access latency. The probabilistic fault tolerance score is assigned based on the initial reliability assessment. Context-aware usage patterns are updated to include the new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['predictive_utility'][key] = INITIAL_PREDICTIVE_UTILITY_SCORE
    metadata['adaptive_latency'][key] = INITIAL_ADAPTIVE_LATENCY_SCORE
    metadata['fault_tolerance'][key] = INITIAL_PROBABILISTIC_FAULT_TOLERANCE_SCORE
    metadata['context_usage'][key] = 1.0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the predictive utility scores of remaining entries are recalibrated to reflect the change in cache composition. The adaptive latency scores are adjusted to account for the new cache state. The probabilistic fault tolerance scores are updated to maintain overall cache reliability. Context-aware usage patterns are refined to improve future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['predictive_utility']:
        del metadata['predictive_utility'][evicted_key]
    if evicted_key in metadata['adaptive_latency']:
        del metadata['adaptive_latency'][evicted_key]
    if evicted_key in metadata['fault_tolerance']:
        del metadata['fault_tolerance'][evicted_key]
    if evicted_key in metadata['context_usage']:
        del metadata['context_usage'][evicted_key]
    
    for key in cache_snapshot.cache:
        metadata['predictive_utility'][key] *= 0.95
        metadata['adaptive_latency'][key] *= 1.05
        metadata['fault_tolerance'][key] *= 0.95
        metadata['context_usage'][key] *= 0.98