# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
INITIAL_TEMPORAL_FEEDBACK_SCORE = 1
INITIAL_QUANTUM_ENTROPY = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains a sequence map of access patterns, predictive state allocations for each cache line, quantum entropy values to measure randomness, and temporal feedback scores to track recency and frequency of accesses.
sequence_map = {}
predictive_state_allocations = {}
quantum_entropy_values = {}
temporal_feedback_scores = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the cache line with the highest quantum entropy value, indicating the least predictable access pattern, and the lowest temporal feedback score, indicating infrequent and non-recent access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_entropy = -1
    min_feedback_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        entropy = quantum_entropy_values.get(key, INITIAL_QUANTUM_ENTROPY)
        feedback_score = temporal_feedback_scores.get(key, INITIAL_TEMPORAL_FEEDBACK_SCORE)
        
        if entropy > max_entropy or (entropy == max_entropy and feedback_score < min_feedback_score):
            max_entropy = entropy
            min_feedback_score = feedback_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the sequence map is updated to reflect the new access pattern, the predictive state allocation is adjusted based on the current state and access, the quantum entropy value is recalculated to account for the new access, and the temporal feedback score is incremented to reflect the recent access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    temporal_feedback_scores[key] = temporal_feedback_scores.get(key, INITIAL_TEMPORAL_FEEDBACK_SCORE) + 1
    # Update sequence map and predictive state allocation
    # For simplicity, we assume these are updated in a straightforward manner
    sequence_map[key] = sequence_map.get(key, []) + [cache_snapshot.access_count]
    predictive_state_allocations[key] = predictive_state_allocations.get(key, 0) + 1
    # Recalculate quantum entropy value
    quantum_entropy_values[key] = 1 / (1 + predictive_state_allocations[key])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the sequence map is updated to include the new access pattern, a predictive state allocation is initialized for the new cache line, the quantum entropy value is set based on initial access randomness, and the temporal feedback score is initialized to a baseline value.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    sequence_map[key] = [cache_snapshot.access_count]
    predictive_state_allocations[key] = 1
    quantum_entropy_values[key] = INITIAL_QUANTUM_ENTROPY
    temporal_feedback_scores[key] = INITIAL_TEMPORAL_FEEDBACK_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the sequence map is pruned to remove the evicted access pattern, the predictive state allocation for the evicted line is discarded, the quantum entropy value is recalculated for the remaining lines, and the temporal feedback scores are adjusted to reflect the removal.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in sequence_map:
        del sequence_map[evicted_key]
    if evicted_key in predictive_state_allocations:
        del predictive_state_allocations[evicted_key]
    if evicted_key in quantum_entropy_values:
        del quantum_entropy_values[evicted_key]
    if evicted_key in temporal_feedback_scores:
        del temporal_feedback_scores[evicted_key]
    
    # Recalculate quantum entropy values for remaining lines
    for key in cache_snapshot.cache:
        predictive_state_allocations[key] = predictive_state_allocations.get(key, 0)
        quantum_entropy_values[key] = 1 / (1 + predictive_state_allocations[key])