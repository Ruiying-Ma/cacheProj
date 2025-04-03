# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, OrderedDict

# Put tunable constant parameters below
INITIAL_HEURISTIC_FUSION_SCORE = 1.0
INITIAL_ADAPTIVE_RESONANCE_LEVEL = 1.0
NEUTRAL_TEMPORAL_DISTORTION_FACTOR = 1.0
BOOST_FACTOR = 1.1
REDUCE_FACTOR = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains a FIFO queue, access frequency, recency, timestamp, resilience score, heuristic fusion score, adaptive resonance level, temporal distortion factor, and a hybrid queue with LRU characteristics.
fifo_queue = deque()
hybrid_queue = OrderedDict()
metadata = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy starts from the front of the FIFO queue and evaluates a combined score of resilience, heuristic fusion, and adaptive resonance adjusted by temporal distortion. The entry with the lowest score is evicted. If scores are tied, the entry at the front of the FIFO queue is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key in fifo_queue:
        meta = metadata[key]
        score = (meta['resilience'] + meta['heuristic_fusion'] + meta['adaptive_resonance']) * meta['temporal_distortion']
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Access frequency is set to 1, recency and timestamp are updated, heuristic fusion score is recalibrated, adaptive resonance level is boosted, temporal distortion factor is reduced, and the entry is moved to the most-recently-used end of the hybrid queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    meta = metadata[key]
    meta['access_frequency'] = 1
    meta['recency'] = cache_snapshot.access_count
    meta['timestamp'] = cache_snapshot.access_count
    meta['heuristic_fusion'] = INITIAL_HEURISTIC_FUSION_SCORE  # Recalibrate
    meta['adaptive_resonance'] *= BOOST_FACTOR
    meta['temporal_distortion'] *= REDUCE_FACTOR
    
    # Move to the most-recently-used end of the hybrid queue
    hybrid_queue.move_to_end(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    Access frequency is set to 1, recency and timestamp are updated, initial heuristic fusion score is calculated, adaptive resonance level is initialized, temporal distortion factor is set to neutral, and the entry is placed at the rear of the FIFO queue and the most-recently-used end of the hybrid queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata[key] = {
        'access_frequency': 1,
        'recency': cache_snapshot.access_count,
        'timestamp': cache_snapshot.access_count,
        'resilience': 1.0,  # Initial resilience score
        'heuristic_fusion': INITIAL_HEURISTIC_FUSION_SCORE,
        'adaptive_resonance': INITIAL_ADAPTIVE_RESONANCE_LEVEL,
        'temporal_distortion': NEUTRAL_TEMPORAL_DISTORTION_FACTOR
    }
    
    fifo_queue.append(key)
    hybrid_queue[key] = obj

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    The entry is removed from the hybrid queue and FIFO queue, heuristic fusion scores are recalculated, adaptive resonance levels are adjusted, and temporal distortion factors are updated.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove from FIFO queue and hybrid queue
    fifo_queue.remove(evicted_key)
    del hybrid_queue[evicted_key]
    
    # Recalculate heuristic fusion scores, adjust adaptive resonance levels, and update temporal distortion factors
    for key in fifo_queue:
        meta = metadata[key]
        meta['heuristic_fusion'] = INITIAL_HEURISTIC_FUSION_SCORE  # Recalibrate
        meta['adaptive_resonance'] *= REDUCE_FACTOR
        meta['temporal_distortion'] *= BOOST_FACTOR
    
    # Remove metadata of evicted object
    del metadata[evicted_key]