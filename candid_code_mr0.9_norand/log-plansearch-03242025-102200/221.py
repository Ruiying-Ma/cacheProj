# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
FIFO_QUEUE_SIZE_LIMIT = 10  # Example size limit for FIFO queue
ACCESS_THRESHOLD = 2  # Threshold for moving objects from FIFO to CLOCK

# Put the metadata specifically maintained by the policy below. The policy maintains a segmented cache with two segments: a FIFO queue for objects accessed only once and a CLOCK queue for frequently accessed objects. Additionally, a Count Bloom Filter is used to approximate the access frequency of each object.
fifo_queue = []
clock_queue = []
clock_pointer = 0
count_bloom_filter = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first checks the FIFO queue for eviction candidates. If the FIFO queue is empty, it uses the CLOCK queue to find the next eviction candidate by traversing in a cyclic manner and evicting the first object with a reference bit of 0.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    global clock_pointer
    candid_obj_key = None
    
    if fifo_queue:
        # Evict from FIFO queue
        candid_obj_key = fifo_queue.pop(0)
    else:
        # Evict from CLOCK queue
        while True:
            clock_obj_key = clock_queue[clock_pointer]
            clock_obj = cache_snapshot.cache[clock_obj_key]
            if clock_obj.reference_bit == 0:
                candid_obj_key = clock_obj_key
                clock_queue.pop(clock_pointer)
                break
            else:
                clock_obj.reference_bit = 0
                clock_pointer = (clock_pointer + 1) % len(clock_queue)
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Count Bloom Filter is updated to increment the access count of the object. If the object is in the FIFO queue and its access count exceeds a threshold, it is moved to the CLOCK queue. The reference bit of the object in the CLOCK queue is set to 1.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    global clock_pointer
    
    # Update Count Bloom Filter
    count_bloom_filter[obj.key] = count_bloom_filter.get(obj.key, 0) + 1
    
    if obj.key in fifo_queue:
        if count_bloom_filter[obj.key] > ACCESS_THRESHOLD:
            # Move from FIFO to CLOCK
            fifo_queue.remove(obj.key)
            clock_queue.append(obj.key)
            obj.reference_bit = 1
    elif obj.key in clock_queue:
        # Set reference bit to 1
        obj.reference_bit = 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is placed in the FIFO queue and the Count Bloom Filter is updated to reflect its initial access count. If the FIFO queue exceeds its size limit, the oldest object is moved to the CLOCK queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Update Count Bloom Filter
    count_bloom_filter[obj.key] = 1
    
    # Insert into FIFO queue
    fifo_queue.append(obj.key)
    
    if len(fifo_queue) > FIFO_QUEUE_SIZE_LIMIT:
        # Move oldest object from FIFO to CLOCK
        oldest_obj_key = fifo_queue.pop(0)
        clock_queue.append(oldest_obj_key)
        cache_snapshot.cache[oldest_obj_key].reference_bit = 0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the Count Bloom Filter is updated to decrement the access count of the evicted object. If the eviction was from the CLOCK queue, the CLOCK pointer is advanced to the next object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    global clock_pointer
    
    # Update Count Bloom Filter
    if evicted_obj.key in count_bloom_filter:
        count_bloom_filter[evicted_obj.key] -= 1
        if count_bloom_filter[evicted_obj.key] <= 0:
            del count_bloom_filter[evicted_obj.key]
    
    if evicted_obj.key in clock_queue:
        # Advance CLOCK pointer
        clock_pointer = (clock_pointer + 1) % len(clock_queue)