# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
FIFO_QUEUE_SIZE = 10  # Example size, can be tuned
COUNTER_THRESHOLD = 3  # Example threshold, can be tuned

# Put the metadata specifically maintained by the policy below. The policy maintains three segments: a FIFO queue for new objects, a CLOCK list for frequently accessed objects, and a counter for each object to track access frequency.
fifo_queue = []
clock_list = []
clock_pointer = 0
counters = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first checks the FIFO queue for eviction candidates. If the FIFO queue is empty, it uses the CLOCK list to find the next eviction candidate by traversing in a cyclic manner and evicting the first object with a counter of zero.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    global clock_pointer

    if fifo_queue:
        candid_obj_key = fifo_queue.pop(0).key
    else:
        while True:
            clock_obj = clock_list[clock_pointer]
            if counters[clock_obj.key] == 0:
                candid_obj_key = clock_obj.key
                clock_list.pop(clock_pointer)
                break
            else:
                counters[clock_obj.key] -= 1
                clock_pointer = (clock_pointer + 1) % len(clock_list)
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the object's counter is incremented. If the object is in the FIFO queue and its counter exceeds a threshold, it is moved to the CLOCK list. The CLOCK pointer is advanced to the next object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    global clock_pointer

    counters[obj.key] += 1

    if obj in fifo_queue and counters[obj.key] > COUNTER_THRESHOLD:
        fifo_queue.remove(obj)
        clock_list.append(obj)
        counters[obj.key] = 0

    clock_pointer = (clock_pointer + 1) % len(clock_list) if clock_list else 0

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is placed in the FIFO queue with a counter set to one. If the FIFO queue is full, the oldest object is moved to the CLOCK list with its counter reset to zero.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    counters[obj.key] = 1

    if len(fifo_queue) >= FIFO_QUEUE_SIZE:
        oldest_obj = fifo_queue.pop(0)
        clock_list.append(oldest_obj)
        counters[oldest_obj.key] = 0

    fifo_queue.append(obj)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy updates the CLOCK pointer to the next object in the CLOCK list. If the evicted object was from the FIFO queue, the next oldest object is moved to the CLOCK list if the FIFO queue is not empty.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    global clock_pointer

    if evicted_obj in fifo_queue:
        if fifo_queue:
            oldest_obj = fifo_queue.pop(0)
            clock_list.append(oldest_obj)
            counters[oldest_obj.key] = 0

    clock_pointer = (clock_pointer + 1) % len(clock_list) if clock_list else 0