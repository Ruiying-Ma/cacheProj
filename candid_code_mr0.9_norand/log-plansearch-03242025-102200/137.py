# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
ONE_TIME_SEGMENT_SIZE = 10  # Example size, can be tuned
CLOCK_SEGMENT_SIZE = 10     # Example size, can be tuned
LFU_SEGMENT_SIZE = 10       # Example size, can be tuned
LRU_SEGMENT_SIZE = 10       # Example size, can be tuned

# Put the metadata specifically maintained by the policy below. The policy maintains four segments: a 'one-time' segment for objects accessed only once, a 'clock' segment for cyclic traversal, an LFU queue for least-frequently-used objects, and an LRU queue for least-recently-used objects. Each segment has its own metadata including access counters, timestamps, and a clock hand pointer.
one_time_segment = {}
clock_segment = {}
lfu_segment = {}
lru_segment = {}
clock_hand = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first attempts to evict from the 'one-time' segment. If no candidates are found, it moves to the 'clock' segment, using the clock hand to find a victim. If still unsuccessful, it checks the LFU queue and finally the LRU queue. The victim is chosen based on the segment's specific criteria.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Evict from one-time segment
    if one_time_segment:
        candid_obj_key = next(iter(one_time_segment))
        del one_time_segment[candid_obj_key]
        return candid_obj_key
    
    # Evict from clock segment
    if clock_segment:
        keys = list(clock_segment.keys())
        while True:
            key = keys[clock_hand]
            if clock_segment[key]['access_count'] == 0:
                candid_obj_key = key
                del clock_segment[candid_obj_key]
                clock_hand = (clock_hand + 1) % len(keys)
                return candid_obj_key
            else:
                clock_segment[key]['access_count'] -= 1
                clock_hand = (clock_hand + 1) % len(keys)
    
    # Evict from LFU segment
    if lfu_segment:
        candid_obj_key = min(lfu_segment, key=lambda k: lfu_segment[k]['access_count'])
        del lfu_segment[candid_obj_key]
        return candid_obj_key
    
    # Evict from LRU segment
    if lru_segment:
        candid_obj_key = next(iter(lru_segment))
        del lru_segment[candid_obj_key]
        return candid_obj_key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access counter and timestamp for the object. If the object is in the 'one-time' segment, it is promoted to the 'clock' segment. The clock hand is advanced in the 'clock' segment. The LFU and LRU queues are updated to reflect the new access frequency and recency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    if key in one_time_segment:
        one_time_segment.pop(key)
        clock_segment[key] = {'access_count': 1, 'timestamp': cache_snapshot.access_count}
    elif key in clock_segment:
        clock_segment[key]['access_count'] += 1
        clock_segment[key]['timestamp'] = cache_snapshot.access_count
    elif key in lfu_segment:
        lfu_segment[key]['access_count'] += 1
        lfu_segment[key]['timestamp'] = cache_snapshot.access_count
    elif key in lru_segment:
        lru_segment.pop(key)
        lru_segment[key] = {'timestamp': cache_snapshot.access_count}

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy places it in the 'one-time' segment with an initial access counter and timestamp. If the 'one-time' segment is full, it evicts the least recently added object. The clock hand, LFU, and LRU metadata are updated to include the new object if it gets promoted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    if len(one_time_segment) >= ONE_TIME_SEGMENT_SIZE:
        evict(cache_snapshot, obj)
    one_time_segment[key] = {'access_count': 0, 'timestamp': cache_snapshot.access_count}

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy updates the metadata by removing the object from its respective segment. If the object was in the 'clock' segment, the clock hand is adjusted accordingly. The LFU and LRU queues are updated to remove the evicted object and maintain their order.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    if key in one_time_segment:
        del one_time_segment[key]
    elif key in clock_segment:
        del clock_segment[key]
        clock_hand = clock_hand % len(clock_segment) if clock_segment else 0
    elif key in lfu_segment:
        del lfu_segment[key]
    elif key in lru_segment:
        del lru_segment[key]