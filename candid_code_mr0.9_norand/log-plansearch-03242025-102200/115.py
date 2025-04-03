# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
DECAY_INTERVAL = 100  # Number of accesses after which decay counters are decremented
INITIAL_DECAY = 10    # Initial decay value for new objects

# Put the metadata specifically maintained by the policy below. The policy maintains three main data structures: a segmented cache with two segments (hot and cold), a decay counter for each object, and a ghost queue to track recently evicted objects.
hot_segment = {}
cold_segment = {}
decay_counters = {}
ghost_queue = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first checks the cold segment for eviction candidates, prioritizing objects with the highest decay values. If no suitable candidates are found, it then checks the hot segment. Evicted objects are recorded in the ghost queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    if cold_segment:
        # Find the object in the cold segment with the highest decay value
        candid_obj_key = max(cold_segment, key=lambda k: decay_counters[k])
    elif hot_segment:
        # If no candidates in cold segment, find the object in the hot segment with the highest decay value
        candid_obj_key = max(hot_segment, key=lambda k: decay_counters[k])
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the decay counter for the accessed object is reset, and the object is moved to the hot segment if it was in the cold segment. The ghost queue is checked to see if the object was recently evicted, and if so, it is given a higher priority in the hot segment.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    obj_key = obj.key
    decay_counters[obj_key] = INITIAL_DECAY
    
    if obj_key in cold_segment:
        # Move object from cold to hot segment
        hot_segment[obj_key] = cold_segment.pop(obj_key)
    
    if obj_key in ghost_queue:
        # Remove from ghost queue if it was recently evicted
        del ghost_queue[obj_key]

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is placed in the cold segment with an initial decay counter. The ghost queue is updated to remove any reference to this object if it was recently evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    obj_key = obj.key
    cold_segment[obj_key] = obj
    decay_counters[obj_key] = INITIAL_DECAY
    
    if obj_key in ghost_queue:
        # Remove from ghost queue if it was recently evicted
        del ghost_queue[obj_key]

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, its metadata is removed from the cache, and the object is added to the ghost queue with a timestamp. The decay counters for remaining objects are periodically decremented to ensure that older objects do not dominate the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    current_time = cache_snapshot.access_count
    
    # Remove metadata of evicted object
    if evicted_key in cold_segment:
        del cold_segment[evicted_key]
    if evicted_key in hot_segment:
        del hot_segment[evicted_key]
    if evicted_key in decay_counters:
        del decay_counters[evicted_key]
    
    # Add evicted object to ghost queue with a timestamp
    ghost_queue[evicted_key] = current_time
    
    # Periodically decrement decay counters
    if current_time % DECAY_INTERVAL == 0:
        for key in decay_counters:
            decay_counters[key] = max(0, decay_counters[key] - 1)