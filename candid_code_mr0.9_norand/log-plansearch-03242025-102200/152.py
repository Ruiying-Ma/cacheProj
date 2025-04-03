# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
FIFO_QUEUE_SIZE = 10
SINGLE_ACCESS_SEGMENT_SIZE = 10

# Put the metadata specifically maintained by the policy below. The policy maintains four segments: a FIFO queue for new entries, a Clock queue for recently accessed entries, an LFU queue for frequently accessed entries, and a segment for single-access entries.
fifo_queue = []
single_access_segment = []
clock_queue = []
lfu_queue = {}
clock_hand = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first checks the single-access segment for eviction candidates. If none are found, it moves to the FIFO queue, then the Clock queue, and finally the LFU queue, evicting the least frequently used item if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Check single-access segment
    if single_access_segment:
        candid_obj_key = single_access_segment.pop(0).key
    # Check FIFO queue
    elif fifo_queue:
        candid_obj_key = fifo_queue.pop(0).key
    # Check Clock queue
    elif clock_queue:
        while True:
            clock_obj = clock_queue[clock_hand]
            if clock_obj['ref_bit'] == 0:
                candid_obj_key = clock_obj['obj'].key
                clock_queue.pop(clock_hand)
                break
            else:
                clock_obj['ref_bit'] = 0
                clock_hand = (clock_hand + 1) % len(clock_queue)
    # Check LFU queue
    else:
        min_freq = min(lfu_queue.values(), key=lambda x: x['freq'])
        for key, value in lfu_queue.items():
            if value['freq'] == min_freq['freq']:
                candid_obj_key = key
                del lfu_queue[key]
                break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    On a cache hit, the object is moved to the Clock queue if it was in the FIFO queue or single-access segment. If it was already in the Clock queue, its reference bit is set. If it was in the LFU queue, its frequency count is incremented.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    obj_key = obj.key
    # Move to Clock queue if in FIFO queue or single-access segment
    if obj in fifo_queue:
        fifo_queue.remove(obj)
        clock_queue.append({'obj': obj, 'ref_bit': 1})
    elif obj in single_access_segment:
        single_access_segment.remove(obj)
        clock_queue.append({'obj': obj, 'ref_bit': 1})
    # Update reference bit if in Clock queue
    else:
        for clock_obj in clock_queue:
            if clock_obj['obj'].key == obj_key:
                clock_obj['ref_bit'] = 1
                break
        # Increment frequency if in LFU queue
        if obj_key in lfu_queue:
            lfu_queue[obj_key]['freq'] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    On inserting a new object, it is placed in the FIFO queue. If the FIFO queue is full, the oldest entry is moved to the single-access segment. If the single-access segment is full, the least recently accessed item is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    if len(fifo_queue) >= FIFO_QUEUE_SIZE:
        oldest_fifo_obj = fifo_queue.pop(0)
        if len(single_access_segment) >= SINGLE_ACCESS_SEGMENT_SIZE:
            single_access_segment.pop(0)
        single_access_segment.append(oldest_fifo_obj)
    fifo_queue.append(obj)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the policy checks the state of the FIFO queue and single-access segment. If the FIFO queue has space, new entries are added there. If the single-access segment has space, it is filled with the oldest FIFO entry. The Clock and LFU queues are updated to reflect the current state of the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Check FIFO queue and single-access segment
    if len(fifo_queue) < FIFO_QUEUE_SIZE:
        fifo_queue.append(obj)
    elif len(single_access_segment) < SINGLE_ACCESS_SEGMENT_SIZE:
        single_access_segment.append(fifo_queue.pop(0))
        fifo_queue.append(obj)
    # Update Clock and LFU queues
    for clock_obj in clock_queue:
        if clock_obj['obj'].key == evicted_obj.key:
            clock_queue.remove(clock_obj)
            break
    if evicted_obj.key in lfu_queue:
        del lfu_queue[evicted_obj.key]