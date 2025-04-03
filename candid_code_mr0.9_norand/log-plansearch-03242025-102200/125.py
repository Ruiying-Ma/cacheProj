# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
SATURATE_LIMIT = 5

# Put the metadata specifically maintained by the policy below. The policy maintains a circular list (clock) of cache entries, a ghost queue for recently evicted items, and a saturate counter for each cache entry to track access frequency up to a predefined limit.
clock_hand = 0
saturate_counters = {}
ghost_queue = []

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy traverses the clock to find the first cache entry with a saturate counter below the limit. If all counters are at the limit, it evicts the entry pointed by the clock hand and moves the hand forward. The evicted entry is added to the ghost queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    global clock_hand
    candid_obj_key = None
    cache_keys = list(cache_snapshot.cache.keys())
    n = len(cache_keys)
    
    while True:
        current_key = cache_keys[clock_hand]
        if saturate_counters[current_key] < SATURATE_LIMIT:
            candid_obj_key = current_key
            break
        clock_hand = (clock_hand + 1) % n
    
    if candid_obj_key is None:
        candid_obj_key = cache_keys[clock_hand]
        clock_hand = (clock_hand + 1) % n
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the saturate counter of the accessed entry is incremented if it is below the limit. The clock hand remains unchanged.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    if saturate_counters[obj.key] < SATURATE_LIMIT:
        saturate_counters[obj.key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    When inserting a new object, the object is added to the position pointed by the clock hand, the saturate counter is initialized to 1, and the clock hand is moved forward. If the ghost queue contains the object, it is removed from the ghost queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    global clock_hand
    if obj.key in ghost_queue:
        ghost_queue.remove(obj.key)
    
    saturate_counters[obj.key] = 1
    clock_hand = (clock_hand + 1) % len(cache_snapshot.cache)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the evicted entry is added to the ghost queue. The clock hand is moved forward to the next entry, and the saturate counter of the new entry is reset to 1.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    global clock_hand
    ghost_queue.append(evicted_obj.key)
    clock_hand = (clock_hand + 1) % len(cache_snapshot.cache)
    saturate_counters[obj.key] = 1