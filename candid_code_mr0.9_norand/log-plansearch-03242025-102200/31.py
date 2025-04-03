# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import OrderedDict

# Put tunable constant parameters below
RECENT_SEGMENT_SIZE = 0.4  # 40% of the cache capacity
FREQUENT_SEGMENT_SIZE = 0.4  # 40% of the cache capacity
GHOST_QUEUE_SIZE = 0.2  # 20% of the cache capacity

# Put the metadata specifically maintained by the policy below. The policy maintains three segments: a 'frequent' segment for frequently accessed objects, a 'recent' segment for recently accessed objects, and a 'ghost' queue for recently evicted objects. Each segment has a fixed size, and objects are moved between segments based on their access patterns.
recent_segment = OrderedDict()
frequent_segment = OrderedDict()
ghost_queue = OrderedDict()

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy evicts objects from the 'recent' segment first. If the 'recent' segment is empty, it evicts from the 'frequent' segment. Evicted objects are added to the 'ghost' queue. If the 'ghost' queue is full, the oldest entry in the 'ghost' queue is removed.
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
    On a cache hit, if the object is in the 'recent' segment, it is moved to the 'frequent' segment. If the object is already in the 'frequent' segment, it remains there. The 'ghost' queue is not affected by cache hits.
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
        # Move to end to mark as most recently used
        frequent_segment.move_to_end(obj.key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    On inserting a new object, it is placed in the 'recent' segment. If the 'recent' segment is full, the least recently used object in the 'recent' segment is evicted to make space. The 'ghost' queue is updated with the evicted object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    recent_segment[obj.key] = obj
    if len(recent_segment) > int(RECENT_SEGMENT_SIZE * cache_snapshot.capacity):
        evicted_key, evicted_obj = recent_segment.popitem(last=False)
        update_after_evict(cache_snapshot, obj, evicted_obj)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the evicted object is added to the 'ghost' queue. If the 'ghost' queue is full, the oldest entry in the 'ghost' queue is removed. The 'recent' and 'frequent' segments are adjusted accordingly to maintain their fixed sizes.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    ghost_queue[evicted_obj.key] = evicted_obj
    if len(ghost_queue) > int(GHOST_QUEUE_SIZE * cache_snapshot.capacity):
        ghost_queue.popitem(last=False)