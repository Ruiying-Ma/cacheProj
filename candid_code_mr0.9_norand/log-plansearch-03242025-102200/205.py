# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

from collections import OrderedDict, deque

# Put tunable constant parameters below
SATURATE_COUNTER_LIMIT = 10
THRESHOLD = 5
GHOST_QUEUE_LIMIT = 100

# Put the metadata specifically maintained by the policy below. The policy maintains three main data structures: a segmented cache with two segments (frequent and recent), a ghost queue for recently evicted objects, and a saturate counter for each object to track access frequency without overflow.
recent_segment = OrderedDict()
frequent_segment = OrderedDict()
ghost_queue = deque()
saturate_counters = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first checks the recent segment for eviction candidates using LRU. If the recent segment is empty, it then checks the frequent segment using LRU. Evicted objects are added to the ghost queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    if recent_segment:
        candid_obj_key, _ = recent_segment.popitem(last=False)
    elif frequent_segment:
        candid_obj_key, _ = frequent_segment.popitem(last=False)
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the object's saturate counter is incremented if it is below the upper limit. If the object is in the recent segment and its counter exceeds a threshold, it is moved to the frequent segment. The LRU position is updated accordingly.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    if key in recent_segment:
        saturate_counters[key] = min(saturate_counters[key] + 1, SATURATE_COUNTER_LIMIT)
        if saturate_counters[key] > THRESHOLD:
            recent_segment.pop(key)
            frequent_segment[key] = obj
    elif key in frequent_segment:
        saturate_counters[key] = min(saturate_counters[key] + 1, SATURATE_COUNTER_LIMIT)
        frequent_segment.move_to_end(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is placed in the recent segment with an initial saturate counter value. The LRU position is updated. If the recent segment is full, the least recently used object is evicted to the ghost queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    if key not in recent_segment and key not in frequent_segment:
        if cache_snapshot.size + obj.size > cache_snapshot.capacity:
            evicted_key = evict(cache_snapshot, obj)
            if evicted_key:
                evicted_obj = cache_snapshot.cache[evicted_key]
                update_after_evict(cache_snapshot, obj, evicted_obj)
        recent_segment[key] = obj
        saturate_counters[key] = 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, it is added to the ghost queue. If the ghost queue is full, the oldest entry in the ghost queue is discarded. The saturate counter for the evicted object is reset.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    ghost_queue.append(evicted_key)
    if len(ghost_queue) > GHOST_QUEUE_LIMIT:
        ghost_queue.popleft()
    if evicted_key in saturate_counters:
        del saturate_counters[evicted_key]