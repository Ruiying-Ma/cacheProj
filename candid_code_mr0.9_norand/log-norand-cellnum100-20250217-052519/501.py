# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, defaultdict
import time

# Put tunable constant parameters below
NEUTRAL_TEMPORAL_DISTORTION = 1.0
INITIAL_ADAPTIVE_RESONANCE = 1.0
HEURISTIC_FUSION_BASE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a FIFO queue, access frequency, recency, timestamp, resilience score, heuristic fusion score, adaptive resonance level, temporal distortion factor, and a hybrid queue with LRU characteristics.
fifo_queue = deque()
hybrid_queue = deque()
access_frequency = defaultdict(int)
recency = {}
timestamp = {}
resilience_score = defaultdict(float)
heuristic_fusion_score = defaultdict(float)
adaptive_resonance_level = defaultdict(float)
temporal_distortion_factor = defaultdict(float)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy evicts the object at the front of the FIFO queue if its access frequency is zero. If not, it evaluates the combined score of resilience, heuristic fusion, and adaptive resonance adjusted by temporal distortion. The entry with the lowest score is evicted. If scores are tied, the entry at the front of the FIFO queue is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    if fifo_queue:
        for key in fifo_queue:
            if access_frequency[key] == 0:
                candid_obj_key = key
                break
        if candid_obj_key is None:
            min_score = float('inf')
            for key in cache_snapshot.cache:
                score = (resilience_score[key] + heuristic_fusion_score[key] + adaptive_resonance_level[key]) * temporal_distortion_factor[key]
                if score < min_score:
                    min_score = score
                    candid_obj_key = key
                elif score == min_score and key == fifo_queue[0]:
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
    # Your code below
    key = obj.key
    access_frequency[key] = 1
    recency[key] = cache_snapshot.access_count
    timestamp[key] = time.time()
    heuristic_fusion_score[key] = HEURISTIC_FUSION_BASE / (1 + recency[key])
    adaptive_resonance_level[key] += 1
    temporal_distortion_factor[key] *= 0.9
    if key in hybrid_queue:
        hybrid_queue.remove(key)
    hybrid_queue.append(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    Access frequency is set to 1, recency and timestamp are updated, initial heuristic fusion score is calculated, adaptive resonance level is initialized, temporal distortion factor is set to neutral, and the entry is placed at the rear of the FIFO queue and the most-recently-used end of the hybrid queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    access_frequency[key] = 1
    recency[key] = cache_snapshot.access_count
    timestamp[key] = time.time()
    heuristic_fusion_score[key] = HEURISTIC_FUSION_BASE / (1 + recency[key])
    adaptive_resonance_level[key] = INITIAL_ADAPTIVE_RESONANCE
    temporal_distortion_factor[key] = NEUTRAL_TEMPORAL_DISTORTION
    fifo_queue.append(key)
    hybrid_queue.append(key)

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
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in fifo_queue:
        fifo_queue.remove(evicted_key)
    if evicted_key in hybrid_queue:
        hybrid_queue.remove(evicted_key)
    del access_frequency[evicted_key]
    del recency[evicted_key]
    del timestamp[evicted_key]
    del resilience_score[evicted_key]
    del heuristic_fusion_score[evicted_key]
    del adaptive_resonance_level[evicted_key]
    del temporal_distortion_factor[evicted_key]
    
    # Recalculate heuristic fusion scores, adaptive resonance levels, and temporal distortion factors for remaining objects
    for key in cache_snapshot.cache:
        heuristic_fusion_score[key] = HEURISTIC_FUSION_BASE / (1 + recency[key])
        adaptive_resonance_level[key] = max(INITIAL_ADAPTIVE_RESONANCE, adaptive_resonance_level[key] - 0.1)
        temporal_distortion_factor[key] *= 1.1