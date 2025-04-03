# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
SATURATE_LIMIT = 5
GHOST_QUEUE_SIZE = 10

# Put the metadata specifically maintained by the policy below. The policy maintains a segmented cache with two segments: a 'recent' segment for newly inserted objects and a 'frequent' segment for objects that have been accessed more than once. It also uses a clock hand to traverse the cache cyclically, a ghost queue to track recently evicted objects, and a saturate counter for each object to count accesses up to a predefined limit.
recent_segment = {}
frequent_segment = {}
saturate_counters = {}
clock_hand = 0
ghost_queue = []

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first attempts to evict objects from the 'recent' segment using the clock hand. If no suitable victim is found, it then looks in the 'frequent' segment. The clock hand ensures that all objects are considered in a cyclic manner. If an object in the 'frequent' segment is evicted, it is added to the ghost queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    global clock_hand
    candid_obj_key = None
    cache_keys = list(cache_snapshot.cache.keys())
    cache_size = len(cache_keys)
    
    while True:
        current_key = cache_keys[clock_hand]
        if current_key in recent_segment:
            candid_obj_key = current_key
            break
        clock_hand = (clock_hand + 1) % cache_size
        if clock_hand == 0:
            break
    
    if candid_obj_key is None:
        while True:
            current_key = cache_keys[clock_hand]
            if current_key in frequent_segment:
                candid_obj_key = current_key
                break
            clock_hand = (clock_hand + 1) % cache_size
            if clock_hand == 0:
                break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the object's saturate counter is incremented up to its limit. If the object is in the 'recent' segment and its counter reaches the threshold, it is moved to the 'frequent' segment. The clock hand is advanced to the next position.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    global clock_hand
    key = obj.key
    if key in saturate_counters:
        saturate_counters[key] = min(saturate_counters[key] + 1, SATURATE_LIMIT)
        if key in recent_segment and saturate_counters[key] == SATURATE_LIMIT:
            recent_segment.pop(key)
            frequent_segment[key] = obj
    clock_hand = (clock_hand + 1) % len(cache_snapshot.cache)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is placed in the 'recent' segment with its saturate counter initialized to 1. The clock hand is advanced to the next position. If the 'recent' segment is full, the policy evicts an object from this segment first.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    global clock_hand
    key = obj.key
    recent_segment[key] = obj
    saturate_counters[key] = 1
    clock_hand = (clock_hand + 1) % len(cache_snapshot.cache)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, if it was from the 'frequent' segment, its identifier is added to the ghost queue. The clock hand is advanced to the next position. The ghost queue is updated to ensure it does not exceed its predefined size, evicting the oldest entries if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    global clock_hand
    key = evicted_obj.key
    if key in frequent_segment:
        ghost_queue.append(key)
        if len(ghost_queue) > GHOST_QUEUE_SIZE:
            ghost_queue.pop(0)
    if key in recent_segment:
        recent_segment.pop(key)
    if key in frequent_segment:
        frequent_segment.pop(key)
    if key in saturate_counters:
        saturate_counters.pop(key)
    clock_hand = (clock_hand + 1) % len(cache_snapshot.cache)