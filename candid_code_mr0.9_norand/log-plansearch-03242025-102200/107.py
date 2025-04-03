# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
INITIAL_DECAY_COUNTER = 3

# Put the metadata specifically maintained by the policy below. The policy maintains a circular list (clock) of cache entries, a decay counter for each entry, and a FIFO queue to track the order of insertion.
clock = []
decay_counters = {}
fifo_queue = []

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy traverses the clock to find the first entry with a decay counter of zero. If no such entry is found, it evicts the oldest entry in the FIFO queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    for key in clock:
        if decay_counters[key] == 0:
            candid_obj_key = key
            break
    
    if candid_obj_key is None:
        candid_obj_key = fifo_queue[0]
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    On a cache hit, the decay counter of the accessed entry is reset to its initial value, and the entry is moved to the back of the FIFO queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    decay_counters[key] = INITIAL_DECAY_COUNTER
    fifo_queue.remove(key)
    fifo_queue.append(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    On inserting a new object, it is added to the clock and the FIFO queue, with its decay counter set to the initial value.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    clock.append(key)
    decay_counters[key] = INITIAL_DECAY_COUNTER
    fifo_queue.append(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the evicted entry is removed from both the clock and the FIFO queue, and the decay counters of all remaining entries are decremented.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    clock.remove(evicted_key)
    fifo_queue.remove(evicted_key)
    del decay_counters[evicted_key]
    
    for key in clock:
        decay_counters[key] -= 1