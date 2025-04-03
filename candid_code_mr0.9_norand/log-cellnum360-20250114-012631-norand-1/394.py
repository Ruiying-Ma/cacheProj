# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
INITIAL_HEURISTIC_FUSION_SCORE = 1.0
INITIAL_ADAPTIVE_RESONANCE_LEVEL = 1.0
ADAPTIVE_RESONANCE_BOOST = 0.1
HEURISTIC_FUSION_RECALIBRATION = 0.05

# Put the metadata specifically maintained by the policy below. The policy maintains a FIFO queue, a circular pointer, access frequency, recency timestamp, heuristic fusion score, and adaptive resonance level.
fifo_queue = []
circular_pointer = 0
access_frequency = {}
recency_timestamp = {}
heuristic_fusion_score = {}
adaptive_resonance_level = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy starts from the current pointer position and evaluates the combined score of frequency, heuristic fusion, and adaptive resonance for each object. It evicts the object with the lowest combined score and resets the pointer to the next position. The evicted object is also removed from the front of the FIFO queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    global circular_pointer
    candid_obj_key = None
    min_combined_score = float('inf')
    
    for i in range(len(fifo_queue)):
        current_key = fifo_queue[(circular_pointer + i) % len(fifo_queue)]
        current_obj = cache_snapshot.cache[current_key]
        combined_score = (access_frequency[current_key] + 
                          heuristic_fusion_score[current_key] + 
                          adaptive_resonance_level[current_key])
        
        if combined_score < min_combined_score:
            min_combined_score = combined_score
            candid_obj_key = current_key
    
    # Update circular pointer to the next position
    circular_pointer = (circular_pointer + 1) % len(fifo_queue)
    
    # Remove the evicted object from the front of the FIFO queue
    fifo_queue.remove(candid_obj_key)
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    The frequency is increased by 1, recency is updated to the current timestamp, the heuristic fusion score is recalibrated, and the adaptive resonance level is boosted. The entry is moved to the rear of the FIFO queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] += 1
    recency_timestamp[key] = cache_snapshot.access_count
    heuristic_fusion_score[key] += HEURISTIC_FUSION_RECALIBRATION
    adaptive_resonance_level[key] += ADAPTIVE_RESONANCE_BOOST
    
    # Move the entry to the rear of the FIFO queue
    fifo_queue.remove(key)
    fifo_queue.append(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    The frequency is set to 1, recency is set to the current timestamp, the heuristic fusion score is set based on initial predictions, and the adaptive resonance level is initialized. The object is placed at the current pointer location and added to the rear of the FIFO queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] = 1
    recency_timestamp[key] = cache_snapshot.access_count
    heuristic_fusion_score[key] = INITIAL_HEURISTIC_FUSION_SCORE
    adaptive_resonance_level[key] = INITIAL_ADAPTIVE_RESONANCE_LEVEL
    
    # Add the object to the rear of the FIFO queue
    fifo_queue.append(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    The heuristic fusion scores of remaining entries are recalculated, and adaptive resonance levels are slightly adjusted. The hybrid queue is updated by removing the evicted entry from the FIFO queue, and the pointer is moved to the next position.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove the evicted object from the metadata
    del access_frequency[evicted_key]
    del recency_timestamp[evicted_key]
    del heuristic_fusion_score[evicted_key]
    del adaptive_resonance_level[evicted_key]
    
    # Recalculate heuristic fusion scores and adjust adaptive resonance levels
    for key in fifo_queue:
        heuristic_fusion_score[key] += HEURISTIC_FUSION_RECALIBRATION
        adaptive_resonance_level[key] += ADAPTIVE_RESONANCE_BOOST