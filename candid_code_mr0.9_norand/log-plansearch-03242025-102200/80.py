# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import OrderedDict

# Put tunable constant parameters below
GHOST_QUEUE_SIZE = 100

# Put the metadata specifically maintained by the policy below. The policy maintains three main data structures: a segmented cache with two segments (frequent and recent), a ghost queue for each segment to track recently evicted objects, and an LRU queue within each segment to manage the order of objects.
recent_segment = OrderedDict()
frequent_segment = OrderedDict()
recent_ghost_queue = OrderedDict()
frequent_ghost_queue = OrderedDict()

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first checks the recent segment for eviction candidates using the LRU queue. If the recent segment is empty or a better candidate is found, it then checks the frequent segment. Evicted objects are moved to their respective ghost queues.
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
    Upon a cache hit, if the object is in the recent segment, it is moved to the frequent segment and updated in the LRU queue. If the object is already in the frequent segment, it is simply updated in the LRU queue to reflect recent access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    if obj.key in recent_segment:
        recent_segment.pop(obj.key)
        frequent_segment[obj.key] = obj
    elif obj.key in frequent_segment:
        frequent_segment.move_to_end(obj.key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is placed in the recent segment and added to the LRU queue. If the recent segment is full, the least recently used object is evicted to its ghost queue, and the new object is inserted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    if cache_snapshot.size + obj.size > cache_snapshot.capacity:
        evicted_key = evict(cache_snapshot, obj)
        if evicted_key:
            evicted_obj = cache_snapshot.cache[evicted_key]
            update_after_evict(cache_snapshot, obj, evicted_obj)
    
    recent_segment[obj.key] = obj

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, it is added to the ghost queue of its respective segment. The ghost queue is updated to ensure it does not exceed its predefined size, evicting the least recently used ghost entries if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in recent_segment:
        recent_ghost_queue[evicted_obj.key] = evicted_obj
        if len(recent_ghost_queue) > GHOST_QUEUE_SIZE:
            recent_ghost_queue.popitem(last=False)
    elif evicted_obj.key in frequent_segment:
        frequent_ghost_queue[evicted_obj.key] = evicted_obj
        if len(frequent_ghost_queue) > GHOST_QUEUE_SIZE:
            frequent_ghost_queue.popitem(last=False)