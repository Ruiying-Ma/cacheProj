# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, defaultdict

# Put tunable constant parameters below
INITIAL_HEURISTIC_SCORE = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a FIFO queue, an LRU queue, frequency count, recency timestamp, and heuristic fusion score for each entry.
fifo_queue = deque()
lru_queue = deque()
frequency_count = defaultdict(int)
recency_timestamp = {}
heuristic_fusion_score = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    During eviction, the policy first considers the front of the FIFO queue. If the entry has a high heuristic fusion score, it evaluates other entries and evicts the one with the lowest combined score of frequency and heuristic fusion.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    while fifo_queue:
        front_key = fifo_queue[0]
        if heuristic_fusion_score[front_key] > INITIAL_HEURISTIC_SCORE:
            break
        fifo_queue.popleft()
        lru_queue.remove(front_key)
        del frequency_count[front_key]
        del recency_timestamp[front_key]
        del heuristic_fusion_score[front_key]
        return front_key

    min_score = float('inf')
    for key in cache_snapshot.cache:
        combined_score = frequency_count[key] + heuristic_fusion_score[key]
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a hit, the frequency is increased by 1, the recency is updated to the current timestamp, the heuristic fusion score is recalibrated, the entry is moved to the most-recently-used end of the LRU queue and the rear of the FIFO queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    frequency_count[key] += 1
    recency_timestamp[key] = cache_snapshot.access_count
    heuristic_fusion_score[key] = frequency_count[key] + recency_timestamp[key]

    if key in lru_queue:
        lru_queue.remove(key)
    lru_queue.append(key)

    if key in fifo_queue:
        fifo_queue.remove(key)
    fifo_queue.append(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its frequency is set to 1, recency is set to the current timestamp, the heuristic fusion score is set based on initial predictions, the object is placed at the most-recently-used end of the LRU queue and the rear of the FIFO queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    frequency_count[key] = 1
    recency_timestamp[key] = cache_snapshot.access_count
    heuristic_fusion_score[key] = INITIAL_HEURISTIC_SCORE

    lru_queue.append(key)
    fifo_queue.append(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, heuristic fusion scores of remaining entries are recalculated, and the hybrid queue is updated by removing the evicted entry from both the LRU and FIFO queues.
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
    if evicted_key in lru_queue:
        lru_queue.remove(evicted_key)
    if evicted_key in frequency_count:
        del frequency_count[evicted_key]
    if evicted_key in recency_timestamp:
        del recency_timestamp[evicted_key]
    if evicted_key in heuristic_fusion_score:
        del heuristic_fusion_score[evicted_key]

    for key in cache_snapshot.cache:
        heuristic_fusion_score[key] = frequency_count[key] + recency_timestamp[key]