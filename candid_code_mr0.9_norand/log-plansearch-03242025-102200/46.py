# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, defaultdict

# Put tunable constant parameters below
ONE_TIME_ACCESS_LIMIT = 100  # Maximum number of objects in the 'One-time Access' segment

# Put the metadata specifically maintained by the policy below. The policy maintains three segments: a 'One-time Access' segment for objects accessed only once, an LFU segment for frequently accessed objects, and an LRU segment for recently accessed objects. Each segment has its own queue and counters.
one_time_access = deque()  # Queue for 'One-time Access' segment
lfu_segment = defaultdict(int)  # Dictionary for LFU segment with frequency counters
lru_segment = deque()  # Queue for LRU segment

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first checks the 'One-time Access' segment for eviction candidates. If this segment is empty, it evicts the least frequently used object from the LFU segment. If the LFU segment is also empty, it evicts the least recently used object from the LRU segment.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    if one_time_access:
        candid_obj_key = one_time_access.popleft()
    elif lfu_segment:
        candid_obj_key = min(lfu_segment, key=lfu_segment.get)
    elif lru_segment:
        candid_obj_key = lru_segment.pop()
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, if the object is in the 'One-time Access' segment, it is moved to the LFU segment and its frequency counter is incremented. If the object is in the LFU segment, its frequency counter is incremented. If the object is in the LRU segment, it is moved to the front of the LRU queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    obj_key = obj.key
    if obj_key in one_time_access:
        one_time_access.remove(obj_key)
        lfu_segment[obj_key] += 1
    elif obj_key in lfu_segment:
        lfu_segment[obj_key] += 1
    elif obj_key in lru_segment:
        lru_segment.remove(obj_key)
        lru_segment.appendleft(obj_key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is placed in the 'One-time Access' segment. If the 'One-time Access' segment is full, the least recently accessed object in this segment is moved to the LFU segment before the new object is inserted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    obj_key = obj.key
    if len(one_time_access) >= ONE_TIME_ACCESS_LIMIT:
        moved_obj_key = one_time_access.popleft()
        lfu_segment[moved_obj_key] += 1
    one_time_access.append(obj_key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy checks if the evicted object was from the 'One-time Access' segment, LFU segment, or LRU segment and updates the respective segment's metadata by removing the object and adjusting counters or pointers as necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_obj_key = evicted_obj.key
    if evicted_obj_key in one_time_access:
        one_time_access.remove(evicted_obj_key)
    elif evicted_obj_key in lfu_segment:
        del lfu_segment[evicted_obj_key]
    elif evicted_obj_key in lru_segment:
        lru_segment.remove(evicted_obj_key)