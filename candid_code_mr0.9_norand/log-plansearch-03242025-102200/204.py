# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, OrderedDict

# Put tunable constant parameters below
GHOST_QUEUE_SIZE = 100  # Maximum size of the ghost queue

# Put the metadata specifically maintained by the policy below. The policy maintains four main structures: a segmented cache with two segments (frequent and recent), a clock hand for cyclic traversal, a ghost queue for recently evicted objects, and an LRU queue within each segment to track usage order.
recent_segment = OrderedDict()
frequent_segment = OrderedDict()
ghost_queue = deque()
clock_hand = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first checking the recent segment using the clock hand. If no suitable victim is found, it moves to the frequent segment. If both segments are exhausted, it evicts the least-recently-used object from the recent segment and updates the ghost queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    global clock_hand
    candid_obj_key = None

    # Check recent segment using clock hand
    keys = list(recent_segment.keys())
    while keys:
        key = keys[clock_hand % len(keys)]
        clock_hand += 1
        if key in recent_segment:
            candid_obj_key = key
            break

    # If no suitable victim found in recent segment, check frequent segment
    if candid_obj_key is None:
        keys = list(frequent_segment.keys())
        while keys:
            key = keys[clock_hand % len(keys)]
            clock_hand += 1
            if key in frequent_segment:
                candid_obj_key = key
                break

    # If both segments are exhausted, evict the LRU object from the recent segment
    if candid_obj_key is None and recent_segment:
        candid_obj_key = next(iter(recent_segment))

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy moves the object to the frequent segment if it was in the recent segment, updates its position in the LRU queue of the frequent segment, and advances the clock hand.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    global clock_hand
    key = obj.key

    if key in recent_segment:
        recent_segment.pop(key)
        frequent_segment[key] = obj
    elif key in frequent_segment:
        frequent_segment.move_to_end(key)

    clock_hand += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy places it in the recent segment, updates the LRU queue of the recent segment, and advances the clock hand. If the recent segment is full, it evicts the LRU object from the recent segment and updates the ghost queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    global clock_hand
    key = obj.key

    if cache_snapshot.size + obj.size > cache_snapshot.capacity:
        evicted_key = evict(cache_snapshot, obj)
        if evicted_key:
            evicted_obj = cache_snapshot.cache[evicted_key]
            update_after_evict(cache_snapshot, obj, evicted_obj)

    recent_segment[key] = obj
    clock_hand += 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy adds the evicted object to the ghost queue, updates the LRU queue of the segment from which the object was evicted, and advances the clock hand. If the ghost queue is full, it removes the oldest entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    global clock_hand
    key = evicted_obj.key

    if key in recent_segment:
        recent_segment.pop(key)
    elif key in frequent_segment:
        frequent_segment.pop(key)

    ghost_queue.append(key)
    if len(ghost_queue) > GHOST_QUEUE_SIZE:
        ghost_queue.popleft()

    clock_hand += 1