# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
QUANTUM_CASCADE_INCREMENT = 1
FREQUENCY_DECAY_FACTOR = 0.9
BASELINE_FREQUENCY = 1
DYNAMIC_WEIGHT_FACTOR = 0.5
COMPOSITE_SCORE_WEIGHTS = {
    'quantum_cascade': 0.4,
    'frequency_modulation': 0.3,
    'dynamic_allocation': 0.2,
    'temporal_synchronization': 0.1
}

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry including a Quantum Cascade score, a Frequency Modulation index, a Dynamic Allocation weight, and a Temporal Synchronization timestamp. The Quantum Cascade score reflects the hierarchical importance of data, the Frequency Modulation index tracks access frequency with a decay factor, the Dynamic Allocation weight adjusts based on cache pressure, and the Temporal Synchronization timestamp records the last access time.
metadata = defaultdict(lambda: {
    'quantum_cascade': 0,
    'frequency_modulation': BASELINE_FREQUENCY,
    'dynamic_allocation': 0,
    'temporal_synchronization': 0
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache entry using a weighted sum of the Quantum Cascade score, Frequency Modulation index, and Dynamic Allocation weight, adjusted by the Temporal Synchronization timestamp. The entry with the lowest composite score is selected for eviction.
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
        composite_score = (
            COMPOSITE_SCORE_WEIGHTS['quantum_cascade'] * meta['quantum_cascade'] +
            COMPOSITE_SCORE_WEIGHTS['frequency_modulation'] * meta['frequency_modulation'] +
            COMPOSITE_SCORE_WEIGHTS['dynamic_allocation'] * meta['dynamic_allocation'] -
            COMPOSITE_SCORE_WEIGHTS['temporal_synchronization'] * meta['temporal_synchronization']
        )
        
        if composite_score < min_score:
            min_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Quantum Cascade score is incremented to reflect increased importance, the Frequency Modulation index is updated to increase frequency with a decay factor, the Dynamic Allocation weight is adjusted based on current cache pressure, and the Temporal Synchronization timestamp is updated to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['quantum_cascade'] += QUANTUM_CASCADE_INCREMENT
    meta['frequency_modulation'] = meta['frequency_modulation'] * FREQUENCY_DECAY_FACTOR + 1
    meta['dynamic_allocation'] = (cache_snapshot.size / cache_snapshot.capacity) * DYNAMIC_WEIGHT_FACTOR
    meta['temporal_synchronization'] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Quantum Cascade score is initialized based on predicted importance, the Frequency Modulation index is set to a baseline frequency, the Dynamic Allocation weight is calculated based on current cache utilization, and the Temporal Synchronization timestamp is set to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['quantum_cascade'] = 1  # Initial predicted importance
    meta['frequency_modulation'] = BASELINE_FREQUENCY
    meta['dynamic_allocation'] = (cache_snapshot.size / cache_snapshot.capacity) * DYNAMIC_WEIGHT_FACTOR
    meta['temporal_synchronization'] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalibrates the Quantum Cascade scores of remaining entries to maintain relative importance, adjusts the Frequency Modulation indices to reflect reduced competition, recalculates Dynamic Allocation weights to optimize space, and updates Temporal Synchronization timestamps to ensure temporal coherence.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        meta['quantum_cascade'] *= 0.9  # Recalibrate importance
        meta['frequency_modulation'] *= FREQUENCY_DECAY_FACTOR
        meta['dynamic_allocation'] = (cache_snapshot.size / cache_snapshot.capacity) * DYNAMIC_WEIGHT_FACTOR
        meta['temporal_synchronization'] = cache_snapshot.access_count