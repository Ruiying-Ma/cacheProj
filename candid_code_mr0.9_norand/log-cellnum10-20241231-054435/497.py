# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_QUANTUM_FREQUENCY_DRIFT = 1.0
INITIAL_ENTROPIC_RECALIBRATION_INDEX = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a heuristic loop counter for each cache entry, a quantum frequency drift value representing the access frequency, a temporal adaptation score indicating the recency of access, and an entropic recalibration index to measure the randomness of access patterns.
metadata = defaultdict(lambda: {
    'heuristic_loop_counter': 0,
    'quantum_frequency_drift': BASELINE_QUANTUM_FREQUENCY_DRIFT,
    'temporal_adaptation_score': 0,
    'entropic_recalibration_index': INITIAL_ENTROPIC_RECALIBRATION_INDEX
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest combined score of quantum frequency drift and temporal adaptation, adjusted by the entropic recalibration index to prioritize entries with more predictable access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        score = (meta['quantum_frequency_drift'] + 
                 (cache_snapshot.access_count - meta['temporal_adaptation_score'])) / meta['entropic_recalibration_index']
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the heuristic loop counter is incremented, the quantum frequency drift is recalibrated to reflect increased access frequency, the temporal adaptation score is updated to the current time, and the entropic recalibration index is adjusted to reflect the reduced randomness of access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['heuristic_loop_counter'] += 1
    meta['quantum_frequency_drift'] += 1
    meta['temporal_adaptation_score'] = cache_snapshot.access_count
    meta['entropic_recalibration_index'] *= 0.9  # Reduce randomness

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the heuristic loop counter is initialized, the quantum frequency drift is set to a baseline value, the temporal adaptation score is set to the current time, and the entropic recalibration index is initialized to reflect initial uncertainty in access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    metadata[obj.key] = {
        'heuristic_loop_counter': 0,
        'quantum_frequency_drift': BASELINE_QUANTUM_FREQUENCY_DRIFT,
        'temporal_adaptation_score': cache_snapshot.access_count,
        'entropic_recalibration_index': INITIAL_ENTROPIC_RECALIBRATION_INDEX
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the heuristic loop counters of remaining entries are decremented to reflect reduced competition, the quantum frequency drift values are recalibrated to account for the change in cache composition, and the entropic recalibration index is adjusted to reflect the new access pattern dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    del metadata[evicted_obj.key]
    
    for key in cache_snapshot.cache:
        meta = metadata[key]
        meta['heuristic_loop_counter'] = max(0, meta['heuristic_loop_counter'] - 1)
        meta['quantum_frequency_drift'] *= 0.95  # Recalibrate drift
        meta['entropic_recalibration_index'] *= 1.1  # Adjust for new dynamics