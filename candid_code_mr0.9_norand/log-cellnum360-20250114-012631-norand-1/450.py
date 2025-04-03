# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
INITIAL_PIS = 1.0
INITIAL_QCE = 1.0
INITIAL_HRI = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a Predictive Inference Score (PIS) for each cache entry, a Quantum Chaos Entropy (QCE) value, a Temporal Phase Calibration (TPC) timestamp, and a Heuristic Relevance Index (HRI).
metadata = {
    'PIS': {},
    'QCE': {},
    'TPC': {},
    'HRI': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest combined score of PIS and HRI, adjusted by the QCE value and the TPC timestamp to account for temporal relevance and chaotic behavior patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = metadata['PIS'][key] + metadata['HRI'][key] - metadata['QCE'][key] + (cache_snapshot.access_count - metadata['TPC'][key])
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the PIS is updated using recent access patterns, the QCE value is recalibrated based on the latest system entropy, the TPC timestamp is refreshed to the current time, and the HRI is adjusted to reflect the increased relevance of the entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['PIS'][key] += 1
    metadata['QCE'][key] = (metadata['QCE'][key] + 1) / 2
    metadata['TPC'][key] = cache_snapshot.access_count
    metadata['HRI'][key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the PIS is initialized based on predictive models, the QCE value is set according to initial system entropy, the TPC timestamp is set to the current time, and the HRI is calculated based on initial heuristic relevance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['PIS'][key] = INITIAL_PIS
    metadata['QCE'][key] = INITIAL_QCE
    metadata['TPC'][key] = cache_snapshot.access_count
    metadata['HRI'][key] = INITIAL_HRI

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalibrates the QCE values of remaining entries to reflect the new system state, updates the TPC timestamps to ensure temporal accuracy, and adjusts the HRI of remaining entries to maintain relevance balance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del metadata['PIS'][evicted_key]
    del metadata['QCE'][evicted_key]
    del metadata['TPC'][evicted_key]
    del metadata['HRI'][evicted_key]
    
    for key in cache_snapshot.cache:
        metadata['QCE'][key] = (metadata['QCE'][key] + 1) / 2
        metadata['TPC'][key] = cache_snapshot.access_count
        metadata['HRI'][key] = max(metadata['HRI'][key] - 1, 0)