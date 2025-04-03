# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
FIFO_QUEUE_SIZE = 10
GHOST_QUEUE_SIZE = 10
SATURATE_COUNTER_LIMIT = 5

# Put the metadata specifically maintained by the policy below. The policy maintains a segmented cache with two segments: a FIFO queue for objects accessed only once and a main cache for frequently accessed objects. It also includes a ghost queue to track recently evicted objects and a saturate counter for each object to limit the maximum count value.
fifo_queue = []
main_cache = {}
ghost_queue = []
saturate_counter = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy evicts objects from the FIFO queue first if it is not empty. If the FIFO queue is empty, it evicts the least recently used object from the main cache. Evicted objects are added to the ghost queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    if fifo_queue:
        candid_obj_key = fifo_queue.pop(0)
    else:
        # Evict the least recently used object from the main cache
        candid_obj_key = min(main_cache, key=lambda k: main_cache[k].access_time)
        del main_cache[candid_obj_key]
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the saturate counter for the object is incremented if it is below the upper limit. If the object is in the FIFO queue, it is moved to the main cache. The ghost queue is checked, and if the object is present, it is removed from the ghost queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    if obj.key in saturate_counter and saturate_counter[obj.key] < SATURATE_COUNTER_LIMIT:
        saturate_counter[obj.key] += 1
    
    if obj.key in fifo_queue:
        fifo_queue.remove(obj.key)
        main_cache[obj.key] = obj
    
    if obj.key in ghost_queue:
        ghost_queue.remove(obj.key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is placed in the FIFO queue. If the FIFO queue is full, the oldest object is evicted to make space. The saturate counter for the new object is initialized to 1.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    if len(fifo_queue) >= FIFO_QUEUE_SIZE:
        evicted_key = fifo_queue.pop(0)
        update_after_evict(cache_snapshot, obj, cache_snapshot.cache[evicted_key])
    
    fifo_queue.append(obj.key)
    saturate_counter[obj.key] = 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, it is added to the ghost queue. If the ghost queue is full, the oldest entry is removed. The saturate counter for the evicted object is reset.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if len(ghost_queue) >= GHOST_QUEUE_SIZE:
        ghost_queue.pop(0)
    
    ghost_queue.append(evicted_obj.key)
    if evicted_obj.key in saturate_counter:
        del saturate_counter[evicted_obj.key]