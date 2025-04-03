# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
PREDICTIVE_ENTROPY_DECREASE = 0.1
INITIAL_PREDICTIVE_ENTROPY = 1.0
NEUTRAL_QUANTUM_FEEDBACK = 0.5
HEURISTIC_LATENCY_ADJUSTMENT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including predictive entropy scores for each cache entry, temporal access patterns, quantum-resilient feedback scores, and heuristic latency adjustments.
metadata = {
    'predictive_entropy': {},  # {obj.key: entropy_score}
    'temporal_access': {},     # {obj.key: last_access_time}
    'quantum_feedback': {},    # {obj.key: feedback_score}
    'latency_adjustment': {}   # {obj.key: latency_adjustment}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache entry with the highest predictive entropy score, indicating the least predictability in future accesses, while also considering temporal access patterns and quantum-resilient feedback to ensure robustness.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_entropy = -1

    for key, cached_obj in cache_snapshot.cache.items():
        entropy_score = metadata['predictive_entropy'].get(key, INITIAL_PREDICTIVE_ENTROPY)
        if entropy_score > max_entropy:
            max_entropy = entropy_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the predictive entropy score by decreasing it slightly, adjusts the temporal access pattern to reflect the recent access, and recalibrates the quantum-resilient feedback score to enhance future predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    if key in metadata['predictive_entropy']:
        metadata['predictive_entropy'][key] = max(0, metadata['predictive_entropy'][key] - PREDICTIVE_ENTROPY_DECREASE)
    metadata['temporal_access'][key] = cache_snapshot.access_count
    metadata['quantum_feedback'][key] = min(1, metadata['quantum_feedback'].get(key, NEUTRAL_QUANTUM_FEEDBACK) + HEURISTIC_LATENCY_ADJUSTMENT)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the predictive entropy score based on initial access patterns, sets the temporal access pattern to the current time, and assigns a neutral quantum-resilient feedback score while applying a heuristic latency adjustment based on initial access latency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['predictive_entropy'][key] = INITIAL_PREDICTIVE_ENTROPY
    metadata['temporal_access'][key] = cache_snapshot.access_count
    metadata['quantum_feedback'][key] = NEUTRAL_QUANTUM_FEEDBACK
    metadata['latency_adjustment'][key] = HEURISTIC_LATENCY_ADJUSTMENT

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalculates the predictive entropy mapping for the remaining entries, updates the temporal integration framework to remove the evicted entry, and adjusts the quantum-resilient feedback scores to reflect the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['predictive_entropy']:
        del metadata['predictive_entropy'][evicted_key]
    if evicted_key in metadata['temporal_access']:
        del metadata['temporal_access'][evicted_key]
    if evicted_key in metadata['quantum_feedback']:
        del metadata['quantum_feedback'][evicted_key]
    if evicted_key in metadata['latency_adjustment']:
        del metadata['latency_adjustment'][evicted_key]

    # Recalculate predictive entropy for remaining entries
    for key in cache_snapshot.cache:
        metadata['predictive_entropy'][key] = max(0, metadata['predictive_entropy'][key] - PREDICTIVE_ENTROPY_DECREASE)