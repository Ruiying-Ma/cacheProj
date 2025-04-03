# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
BASELINE_TEMPORAL_ANOMALY_SCORE = 1.0
INITIAL_QUANTUM_INTERFERENCE_PATTERN_INDEX = 0.5
DEFAULT_ADAPTIVE_PRIORITY_INDEX = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive context map for each cache entry, a temporal anomaly score, a quantum interference pattern index, and an adaptive priority index.
predictive_context_map = {}
temporal_anomaly_scores = {}
quantum_interference_pattern_indices = {}
adaptive_priority_indices = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the entry with the highest temporal anomaly score, lowest quantum interference pattern index, and lowest adaptive priority index.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_temporal_anomaly_score = -1
    min_quantum_interference_pattern_index = float('inf')
    min_adaptive_priority_index = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        tas = temporal_anomaly_scores.get(key, BASELINE_TEMPORAL_ANOMALY_SCORE)
        qipi = quantum_interference_pattern_indices.get(key, INITIAL_QUANTUM_INTERFERENCE_PATTERN_INDEX)
        api = adaptive_priority_indices.get(key, DEFAULT_ADAPTIVE_PRIORITY_INDEX)

        if (tas > max_temporal_anomaly_score or
            (tas == max_temporal_anomaly_score and qipi < min_quantum_interference_pattern_index) or
            (tas == max_temporal_anomaly_score and qipi == min_quantum_interference_pattern_index and api < min_adaptive_priority_index)):
            max_temporal_anomaly_score = tas
            min_quantum_interference_pattern_index = qipi
            min_adaptive_priority_index = api
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive context map is updated based on recent access patterns, the temporal anomaly score is recalculated, the quantum interference pattern index is adjusted to reflect the new access, and the adaptive priority index is incremented.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    # Update predictive context map
    predictive_context_map[key] = cache_snapshot.access_count

    # Recalculate temporal anomaly score
    temporal_anomaly_scores[key] = 1.0 / (cache_snapshot.access_count - predictive_context_map[key] + 1)

    # Adjust quantum interference pattern index
    quantum_interference_pattern_indices[key] = min(1.0, quantum_interference_pattern_indices.get(key, INITIAL_QUANTUM_INTERFERENCE_PATTERN_INDEX) + 0.1)

    # Increment adaptive priority index
    adaptive_priority_indices[key] = adaptive_priority_indices.get(key, DEFAULT_ADAPTIVE_PRIORITY_INDEX) + 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the predictive context map is initialized, the temporal anomaly score is set to a baseline value, the quantum interference pattern index is set based on initial access probability, and the adaptive priority index is set to a default starting value.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    # Initialize predictive context map
    predictive_context_map[key] = cache_snapshot.access_count

    # Set temporal anomaly score to baseline value
    temporal_anomaly_scores[key] = BASELINE_TEMPORAL_ANOMALY_SCORE

    # Set quantum interference pattern index based on initial access probability
    quantum_interference_pattern_indices[key] = INITIAL_QUANTUM_INTERFERENCE_PATTERN_INDEX

    # Set adaptive priority index to default starting value
    adaptive_priority_indices[key] = DEFAULT_ADAPTIVE_PRIORITY_INDEX

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the predictive context map is adjusted to remove the evicted entry, the temporal anomaly scores of remaining entries are recalculated, the quantum interference pattern index is normalized, and the adaptive priority index of remaining entries is adjusted to reflect the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Remove evicted entry from predictive context map
    if evicted_key in predictive_context_map:
        del predictive_context_map[evicted_key]

    # Remove evicted entry from temporal anomaly scores
    if evicted_key in temporal_anomaly_scores:
        del temporal_anomaly_scores[evicted_key]

    # Remove evicted entry from quantum interference pattern indices
    if evicted_key in quantum_interference_pattern_indices:
        del quantum_interference_pattern_indices[evicted_key]

    # Remove evicted entry from adaptive priority indices
    if evicted_key in adaptive_priority_indices:
        del adaptive_priority_indices[evicted_key]

    # Recalculate temporal anomaly scores for remaining entries
    for key in cache_snapshot.cache:
        temporal_anomaly_scores[key] = 1.0 / (cache_snapshot.access_count - predictive_context_map[key] + 1)

    # Normalize quantum interference pattern index for remaining entries
    total_qipi = sum(quantum_interference_pattern_indices.values())
    for key in quantum_interference_pattern_indices:
        quantum_interference_pattern_indices[key] /= total_qipi

    # Adjust adaptive priority index for remaining entries
    for key in adaptive_priority_indices:
        adaptive_priority_indices[key] = max(1, adaptive_priority_indices[key] - 1)