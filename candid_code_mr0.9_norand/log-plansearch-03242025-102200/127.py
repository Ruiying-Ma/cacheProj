# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
INITIAL_DECAY_FACTOR = 1.0
SATURATE_COUNTER_LIMIT = 10
DECAY_RATE = 0.9
GHOST_QUEUE_LIMIT = 100

# Put the metadata specifically maintained by the policy below. The policy maintains a decay factor for each object, a ghost queue to track recently evicted objects, and a saturate counter for each object to limit its maximum value.
decay_factors = {}
saturate_counters = {}
ghost_queue = []

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on the lowest combined score of the decayed value and the saturate counter, ensuring that objects with low recent usage and low historical importance are evicted first.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = decay_factors[key] + saturate_counters[key]
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the object's decay factor is reset to its initial value, and its saturate counter is incremented but capped at the predefined upper limit.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    decay_factors[obj.key] = INITIAL_DECAY_FACTOR
    saturate_counters[obj.key] = min(saturate_counters[obj.key] + 1, SATURATE_COUNTER_LIMIT)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its decay factor and saturate counter, and checks the ghost queue to see if the object was recently evicted, giving it a higher initial priority if found.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    decay_factors[obj.key] = INITIAL_DECAY_FACTOR
    saturate_counters[obj.key] = 0
    
    for ghost_obj_key, timestamp in ghost_queue:
        if ghost_obj_key == obj.key:
            saturate_counters[obj.key] = SATURATE_COUNTER_LIMIT // 2
            break

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy adds the evicted object to the ghost queue with a timestamp, and periodically decays the values of all objects in the cache to prevent aging issues.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    ghost_queue.append((evicted_obj.key, cache_snapshot.access_count))
    if len(ghost_queue) > GHOST_QUEUE_LIMIT:
        ghost_queue.pop(0)
    
    for key in decay_factors:
        decay_factors[key] *= DECAY_RATE