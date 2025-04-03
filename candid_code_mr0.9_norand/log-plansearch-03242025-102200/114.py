# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
RECENT_SEGMENT_SIZE = 0.5  # Fraction of the cache capacity allocated to the recent segment
FREQUENT_SEGMENT_SIZE = 0.5  # Fraction of the cache capacity allocated to the frequent segment
SATURATE_COUNTER_LIMIT = 10  # Upper limit for the saturate counter
THRESHOLD = 5  # Threshold for moving objects from recent to frequent segment
GHOST_QUEUE_LIMIT = 100  # Maximum size of the ghost queue

# Put the metadata specifically maintained by the policy below. The policy maintains three main structures: a segmented cache with two segments (frequent and recent), a ghost queue for each segment, and a saturate counter for each object in the cache to track access frequency.
recent_segment = {}
frequent_segment = {}
recent_ghost_queue = []
frequent_ghost_queue = []
saturate_counter = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first attempts to evict from the recent segment. If the recent segment is empty, it evicts from the frequent segment. Evicted objects are added to their respective ghost queues.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    if recent_segment:
        # Evict the least recently used object from the recent segment
        candid_obj_key = next(iter(recent_segment))
    elif frequent_segment:
        # Evict the least recently used object from the frequent segment
        candid_obj_key = next(iter(frequent_segment))
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the saturate counter for the object is incremented if it is below the upper limit. If the object is in the recent segment and its counter exceeds a threshold, it is moved to the frequent segment.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    if key in saturate_counter:
        if saturate_counter[key] < SATURATE_COUNTER_LIMIT:
            saturate_counter[key] += 1
        if key in recent_segment and saturate_counter[key] > THRESHOLD:
            # Move the object from recent to frequent segment
            frequent_segment[key] = recent_segment.pop(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is placed in the recent segment with its saturate counter initialized to 1. If the recent segment is full, the least recently used object is evicted to make space.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    recent_segment[key] = obj
    saturate_counter[key] = 1
    if sum(o.size for o in recent_segment.values()) > cache_snapshot.capacity * RECENT_SEGMENT_SIZE:
        # Evict the least recently used object from the recent segment
        evicted_key = next(iter(recent_segment))
        evicted_obj = recent_segment.pop(evicted_key)
        update_after_evict(cache_snapshot, obj, evicted_obj)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, it is added to the ghost queue of its respective segment. If the ghost queue is full, the oldest entry is removed. The saturate counter of the evicted object is reset.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    key = evicted_obj.key
    if key in recent_segment:
        recent_ghost_queue.append(key)
        if len(recent_ghost_queue) > GHOST_QUEUE_LIMIT:
            recent_ghost_queue.pop(0)
    elif key in frequent_segment:
        frequent_ghost_queue.append(key)
        if len(frequent_ghost_queue) > GHOST_QUEUE_LIMIT:
            frequent_ghost_queue.pop(0)
    if key in saturate_counter:
        del saturate_counter[key]