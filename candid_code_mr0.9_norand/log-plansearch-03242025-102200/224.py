# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
GHOST_QUEUE_SIZE = 100

# Put the metadata specifically maintained by the policy below. The policy maintains a segmented cache with two segments: a 'frequent' segment and a 'recent' segment. It also maintains a clock hand for cyclic traversal, a FIFO queue for the 'recent' segment, and a ghost queue to track recently evicted objects.
recent_segment = []
frequent_segment = {}
reference_bits = {}
clock_hand = 0
ghost_queue = []

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first checks the 'recent' segment for eviction candidates using the FIFO queue. If no candidates are found, it uses the clock hand to traverse the 'frequent' segment cyclically, evicting the first object with a reference bit of 0. If the object is in the ghost queue, it is given a second chance and moved to the 'frequent' segment.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    global clock_hand
    candid_obj_key = None

    # Check the 'recent' segment for eviction candidates using the FIFO queue
    if recent_segment:
        candid_obj_key = recent_segment.pop(0)
    else:
        # Use the clock hand to traverse the 'frequent' segment cyclically
        keys = list(frequent_segment.keys())
        while True:
            key = keys[clock_hand]
            if reference_bits[key] == 0:
                candid_obj_key = key
                break
            else:
                reference_bits[key] = 0
                clock_hand = (clock_hand + 1) % len(keys)

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, if the object is in the 'recent' segment, it is moved to the 'frequent' segment and its reference bit is set to 1. The clock hand is advanced. If the object is already in the 'frequent' segment, its reference bit is set to 1 and the clock hand is advanced.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    global clock_hand

    if obj.key in recent_segment:
        recent_segment.remove(obj.key)
        frequent_segment[obj.key] = obj
        reference_bits[obj.key] = 1
    elif obj.key in frequent_segment:
        reference_bits[obj.key] = 1

    clock_hand = (clock_hand + 1) % len(frequent_segment)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is placed in the 'recent' segment and added to the FIFO queue. If the 'recent' segment is full, the oldest object is moved to the 'frequent' segment if it is not in the ghost queue, otherwise it is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    if len(recent_segment) * obj.size >= cache_snapshot.capacity // 2:
        oldest_key = recent_segment.pop(0)
        if oldest_key not in ghost_queue:
            frequent_segment[oldest_key] = cache_snapshot.cache[oldest_key]
            reference_bits[oldest_key] = 0
        else:
            del cache_snapshot.cache[oldest_key]

    recent_segment.append(obj.key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, it is added to the ghost queue. If the ghost queue is full, the oldest entry is removed. The clock hand is advanced if the eviction was from the 'frequent' segment.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    global clock_hand

    ghost_queue.append(evicted_obj.key)
    if len(ghost_queue) > GHOST_QUEUE_SIZE:
        ghost_queue.pop(0)

    if evicted_obj.key in frequent_segment:
        clock_hand = (clock_hand + 1) % len(frequent_segment)