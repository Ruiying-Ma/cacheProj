# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
DEFAULT_LATENCY_THRESHOLD = 100
DEFAULT_QUANTUM_INDEX = 1
DEFAULT_TEMPORAL_INVERSION_SCORE = 50
DEFAULT_HEURISTIC_LEARNING_RATE = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive latency threshold for each cache entry, a quantum synchronization index to track access patterns, a temporal inversion score to measure the recency and frequency of accesses, and a heuristic learning rate to adaptively adjust the other metadata values.
metadata = {
    'latency_threshold': {},
    'quantum_index': {},
    'temporal_inversion_score': {},
    'heuristic_learning_rate': DEFAULT_HEURISTIC_LEARNING_RATE
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the cache entry with the highest temporal inversion score, indicating it is the least recently and frequently accessed, while also considering entries that exceed the predictive latency threshold.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_inversion_score = -1

    for key, cached_obj in cache_snapshot.cache.items():
        if metadata['temporal_inversion_score'][key] > max_inversion_score:
            max_inversion_score = metadata['temporal_inversion_score'][key]
            candid_obj_key = key
        elif metadata['temporal_inversion_score'][key] == max_inversion_score:
            if metadata['latency_threshold'][key] < metadata['latency_threshold'][candid_obj_key]:
                candid_obj_key = key

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy decreases the temporal inversion score for the accessed entry, adjusts the quantum synchronization index to reflect the current access pattern, and updates the predictive latency threshold based on the heuristic learning rate.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['temporal_inversion_score'][key] = max(0, metadata['temporal_inversion_score'][key] - 1)
    metadata['quantum_index'][key] += 1
    metadata['latency_threshold'][key] = max(1, metadata['latency_threshold'][key] * (1 - metadata['heuristic_learning_rate']))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the predictive latency threshold, sets the quantum synchronization index to a default value, assigns a moderate temporal inversion score, and calibrates the heuristic learning rate to ensure balanced adaptation.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['latency_threshold'][key] = DEFAULT_LATENCY_THRESHOLD
    metadata['quantum_index'][key] = DEFAULT_QUANTUM_INDEX
    metadata['temporal_inversion_score'][key] = DEFAULT_TEMPORAL_INVERSION_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the predictive latency thresholds for remaining entries, adjusts the quantum synchronization indices to account for the change in cache composition, and fine-tunes the heuristic learning rate to improve future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['latency_threshold']:
        del metadata['latency_threshold'][evicted_key]
    if evicted_key in metadata['quantum_index']:
        del metadata['quantum_index'][evicted_key]
    if evicted_key in metadata['temporal_inversion_score']:
        del metadata['temporal_inversion_score'][evicted_key]

    for key in cache_snapshot.cache:
        metadata['latency_threshold'][key] = max(1, metadata['latency_threshold'][key] * (1 + metadata['heuristic_learning_rate']))
        metadata['quantum_index'][key] = max(1, metadata['quantum_index'][key] - 1)