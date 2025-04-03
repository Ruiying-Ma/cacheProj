# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

from collections import deque, defaultdict

# Put tunable constant parameters below
FIFO_QUEUE_SIZE_LIMIT = 10  # Maximum number of objects in the FIFO queue
LFU_DECAY_FACTOR = 0.9  # Decay factor for aging in the LFU queue
FREQUENCY_THRESHOLD = 5  # Frequency threshold to move an object from FIFO to LFU

# Put the metadata specifically maintained by the policy below. The policy maintains four segments: a FIFO queue for new objects, an LFU queue for frequently accessed objects, a decay factor for aging, and a counter for access frequency.
fifo_queue = deque()
lfu_queue = {}
access_frequency = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first checks the FIFO queue for eviction candidates. If the FIFO queue is empty, it checks the LFU queue. Objects in the LFU queue are periodically decayed to ensure that older objects do not dominate.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    if fifo_queue:
        candid_obj_key = fifo_queue.popleft().key
    else:
        # Apply decay to LFU queue
        for key in lfu_queue:
            access_frequency[key] *= LFU_DECAY_FACTOR
        # Find the least frequently used object
        candid_obj_key = min(lfu_queue, key=lambda k: access_frequency[k])
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency counter for the object is incremented. If the object is in the FIFO queue and reaches a certain frequency threshold, it is moved to the LFU queue. The decay factor is applied to all objects in the LFU queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    access_frequency[obj.key] += 1
    if obj in fifo_queue:
        if access_frequency[obj.key] >= FREQUENCY_THRESHOLD:
            fifo_queue.remove(obj)
            lfu_queue[obj.key] = obj
    else:
        # Apply decay to LFU queue
        for key in lfu_queue:
            access_frequency[key] *= LFU_DECAY_FACTOR

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    Upon inserting a new object, it is placed in the FIFO queue. The FIFO queue is checked for overflow, and if it exceeds its size limit, the oldest object is moved to the LFU queue or evicted if the LFU queue is also full.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    fifo_queue.append(obj)
    if len(fifo_queue) > FIFO_QUEUE_SIZE_LIMIT:
        oldest_obj = fifo_queue.popleft()
        lfu_queue[oldest_obj.key] = oldest_obj

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the metadata is updated by removing the evicted object from the appropriate queue. The decay factor is recalculated to ensure it remains balanced, and the access frequency counters are adjusted accordingly.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in fifo_queue:
        fifo_queue.remove(evicted_obj)
    elif evicted_obj.key in lfu_queue:
        del lfu_queue[evicted_obj.key]
    if evicted_obj.key in access_frequency:
        del access_frequency[evicted_obj.key]