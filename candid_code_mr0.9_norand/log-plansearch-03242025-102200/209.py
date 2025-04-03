# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
SATURATE_LIMIT = 5

# Put the metadata specifically maintained by the policy below. The policy maintains a segmented cache with two segments: a 'recently used' segment and a 'frequently used' segment. Each segment has its own LRU queue. Additionally, each object has a decay counter and a saturate counter.
recently_used = {}
frequently_used = {}
decay_counters = {}
saturate_counters = {}
lru_recently_used = []
lru_frequently_used = []

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first checks the 'recently used' segment for eviction candidates. If no suitable candidate is found, it then checks the 'frequently used' segment. Within each segment, the object with the highest decay counter is chosen for eviction. If there is a tie, the LRU queue is used to break the tie.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    def find_eviction_candidate(segment, lru_queue):
        if not segment:
            return None
        max_decay = max(decay_counters[key] for key in segment)
        candidates = [key for key in segment if decay_counters[key] == max_decay]
        for key in lru_queue:
            if key in candidates:
                return key
        return None

    candid_obj_key = find_eviction_candidate(recently_used, lru_recently_used)
    if candid_obj_key is None:
        candid_obj_key = find_eviction_candidate(frequently_used, lru_frequently_used)
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the object's decay counter is reset, and its saturate counter is incremented up to its predefined limit. The object is moved to the 'frequently used' segment if it is not already there. The LRU queue for the relevant segment is updated to reflect the recent access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    decay_counters[key] = 0
    saturate_counters[key] = min(saturate_counters[key] + 1, SATURATE_LIMIT)
    
    if key in recently_used:
        recently_used.pop(key)
        lru_recently_used.remove(key)
        frequently_used[key] = obj
        lru_frequently_used.append(key)
    else:
        lru_frequently_used.remove(key)
        lru_frequently_used.append(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is placed in the 'recently used' segment with its decay counter initialized and its saturate counter set to zero. The LRU queue for the 'recently used' segment is updated to include the new object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    recently_used[key] = obj
    decay_counters[key] = 0
    saturate_counters[key] = 0
    lru_recently_used.append(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy decrements the decay counters of all remaining objects in the same segment. The LRU queue for the relevant segment is updated to remove the evicted object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    key = evicted_obj.key
    if key in recently_used:
        recently_used.pop(key)
        lru_recently_used.remove(key)
        for k in recently_used:
            decay_counters[k] -= 1
    elif key in frequently_used:
        frequently_used.pop(key)
        lru_frequently_used.remove(key)
        for k in frequently_used:
            decay_counters[k] -= 1