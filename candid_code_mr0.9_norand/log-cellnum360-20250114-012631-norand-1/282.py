# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
INITIAL_PREDICTIVE_GRADIENT = 1
NEUTRAL_QUANTUM_PHASE_MODULATION = 0
INITIAL_STOCHASTIC_COHERENCE = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive gradient score for each cache entry, a quantum phase modulation index, a stochastic coherence value, and a temporal fidelity timestamp.
metadata = {
    'predictive_gradient': {},
    'quantum_phase_modulation': {},
    'stochastic_coherence': {},
    'temporal_fidelity': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest combined score of predictive gradient and stochastic coherence, adjusted by the quantum phase modulation index and temporal fidelity.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (metadata['predictive_gradient'][key] + metadata['stochastic_coherence'][key] 
                          - metadata['quantum_phase_modulation'][key] + metadata['temporal_fidelity'][key])
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive gradient score is increased, the quantum phase modulation index is recalibrated, the stochastic coherence value is reinforced, and the temporal fidelity timestamp is updated to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['predictive_gradient'][key] += 1
    metadata['quantum_phase_modulation'][key] = (metadata['quantum_phase_modulation'][key] + 1) % 10
    metadata['stochastic_coherence'][key] += 1
    metadata['temporal_fidelity'][key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the predictive gradient score is initialized based on recent access patterns, the quantum phase modulation index is set to a neutral state, the stochastic coherence value is randomized within a coherent range, and the temporal fidelity timestamp is set to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['predictive_gradient'][key] = INITIAL_PREDICTIVE_GRADIENT
    metadata['quantum_phase_modulation'][key] = NEUTRAL_QUANTUM_PHASE_MODULATION
    metadata['stochastic_coherence'][key] = INITIAL_STOCHASTIC_COHERENCE
    metadata['temporal_fidelity'][key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the predictive gradient scores of remaining entries are adjusted to reflect the new cache state, the quantum phase modulation indices are slightly perturbed, the stochastic coherence values are recalculated, and the temporal fidelity timestamps are normalized.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del metadata['predictive_gradient'][evicted_key]
    del metadata['quantum_phase_modulation'][evicted_key]
    del metadata['stochastic_coherence'][evicted_key]
    del metadata['temporal_fidelity'][evicted_key]
    
    for key in cache_snapshot.cache:
        metadata['predictive_gradient'][key] = max(1, metadata['predictive_gradient'][key] - 1)
        metadata['quantum_phase_modulation'][key] = (metadata['quantum_phase_modulation'][key] + 1) % 10
        metadata['stochastic_coherence'][key] = max(1, metadata['stochastic_coherence'][key] - 1)
        metadata['temporal_fidelity'][key] = cache_snapshot.access_count