# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
from collections import deque, defaultdict

# Put tunable constant parameters below
HEURISTIC_FUSION_FACTOR = 1.0
ADAPTIVE_RESONANCE_FACTOR = 1.0
TEMPORAL_DISTORTION_FACTOR = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a FIFO queue, an LRU queue, access frequency, recency timestamp, and a combined score for each entry. The combined score is calculated using heuristic fusion, adaptive resonance, and temporal distortion factors.
fifo_queue = deque()
lru_queue = deque()
access_frequency = defaultdict(int)
recency_timestamp = defaultdict(int)
combined_score = defaultdict(float)

def calculate_combined_score(freq, recency, current_time):
    return (HEURISTIC_FUSION_FACTOR * freq +
            ADAPTIVE_RESONANCE_FACTOR * (current_time - recency) +
            TEMPORAL_DISTORTION_FACTOR * (1 / (current_time - recency + 1)))

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first checks the front of the FIFO queue. If the combined score of the front entry is high, it evaluates other entries and evicts the one with the lowest combined score. If the front entry has a low combined score, it is evicted directly.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    front_key = fifo_queue[0]
    front_score = combined_score[front_key]
    
    if front_score > 0.5:  # Assuming 0.5 as a threshold for high score
        min_score = float('inf')
        for key in cache_snapshot.cache:
            if combined_score[key] < min_score:
                min_score = combined_score[key]
                candid_obj_key = key
    else:
        candid_obj_key = front_key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    The frequency is increased by 1, the recency is updated to the current timestamp, the combined score is recalculated, and the entry is moved to the most-recently-used end of the LRU queue and the rear of the FIFO queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] += 1
    recency_timestamp[key] = cache_snapshot.access_count
    combined_score[key] = calculate_combined_score(access_frequency[key], recency_timestamp[key], cache_snapshot.access_count)
    
    if key in lru_queue:
        lru_queue.remove(key)
    lru_queue.append(key)
    
    if key in fifo_queue:
        fifo_queue.remove(key)
    fifo_queue.append(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    The frequency is set to 1, recency is set to the current timestamp, the combined score is initialized based on initial predictions, and the object is placed at the most-recently-used end of the LRU queue and the rear of the FIFO queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] = 1
    recency_timestamp[key] = cache_snapshot.access_count
    combined_score[key] = calculate_combined_score(access_frequency[key], recency_timestamp[key], cache_snapshot.access_count)
    
    lru_queue.append(key)
    fifo_queue.append(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    The combined scores of remaining entries are recalculated, and the hybrid queue is updated by removing the evicted entry from both the LRU and FIFO queues.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in lru_queue:
        lru_queue.remove(evicted_key)
    if evicted_key in fifo_queue:
        fifo_queue.remove(evicted_key)
    
    del access_frequency[evicted_key]
    del recency_timestamp[evicted_key]
    del combined_score[evicted_key]
    
    for key in cache_snapshot.cache:
        combined_score[key] = calculate_combined_score(access_frequency[key], recency_timestamp[key], cache_snapshot.access_count)