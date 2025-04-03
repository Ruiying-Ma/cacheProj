# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
INITIAL_DECAY_COUNTER = 3
GHOST_QUEUE_MAX_SIZE = 100

# Put the metadata specifically maintained by the policy below. The policy maintains a circular buffer for the clock mechanism, a decay counter for each cache entry, a FIFO queue for insertion order, and a ghost queue to track recently evicted items.
clock_buffer = []
decay_counters = {}
fifo_queue = []
ghost_queue = []

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by traversing the clock buffer cyclically, preferring entries with the lowest decay counter. If all entries have the same decay counter, it evicts the oldest entry based on the FIFO queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_decay = min(decay_counters.values())
    for key in clock_buffer:
        if decay_counters[key] == min_decay:
            candid_obj_key = key
            break
    if candid_obj_key is None:
        candid_obj_key = fifo_queue[0]
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the decay counter for the accessed entry is reset to its initial value, and the entry is moved to the back of the FIFO queue to reflect its recent use.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    decay_counters[obj.key] = INITIAL_DECAY_COUNTER
    fifo_queue.remove(obj.key)
    fifo_queue.append(obj.key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the object is added to the clock buffer with an initial decay counter, appended to the FIFO queue, and the ghost queue is checked to see if the object was recently evicted, potentially adjusting its priority.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    clock_buffer.append(obj.key)
    decay_counters[obj.key] = INITIAL_DECAY_COUNTER
    fifo_queue.append(obj.key)
    for ghost in ghost_queue:
        if ghost['key'] == obj.key:
            decay_counters[obj.key] += 1
            ghost_queue.remove(ghost)
            break

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the entry is removed from the clock buffer and FIFO queue, and its metadata is added to the ghost queue with a timestamp to track its recent eviction, ensuring it can be reconsidered for cache re-entry if accessed soon.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    clock_buffer.remove(evicted_obj.key)
    fifo_queue.remove(evicted_obj.key)
    del decay_counters[evicted_obj.key]
    ghost_queue.append({'key': evicted_obj.key, 'timestamp': cache_snapshot.access_count})
    if len(ghost_queue) > GHOST_QUEUE_MAX_SIZE:
        ghost_queue.pop(0)