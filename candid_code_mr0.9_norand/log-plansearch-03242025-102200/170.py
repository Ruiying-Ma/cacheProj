# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
RECENTLY_ACCESSED_LIMIT = 5
LFU_LIMIT = 10
GHOST_QUEUE_LIMIT = 15
SATURATE_THRESHOLD = 3

# Put the metadata specifically maintained by the policy below. The policy maintains a segmented cache with three segments: a 'recently accessed' segment, an LFU segment, and a ghost queue. Each segment has a saturate counter to track access frequency. The ghost queue records recently evicted objects with their access frequencies.
recently_accessed = {}
lfu_segment = {}
ghost_queue = []

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first checks the 'recently accessed' segment for eviction candidates. If none are found, it checks the LFU segment. If both segments are full, it evicts the least frequently used object from the LFU segment. The evicted object's metadata is moved to the ghost queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    if recently_accessed:
        candid_obj_key = min(recently_accessed, key=lambda k: recently_accessed[k]['access_count'])
    elif lfu_segment:
        candid_obj_key = min(lfu_segment, key=lambda k: lfu_segment[k]['access_count'])
    else:
        candid_obj_key = min(cache_snapshot.cache, key=lambda k: cache_snapshot.cache[k].size)
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the object's saturate counter is incremented (up to its predefined limit). If the object is in the 'recently accessed' segment and its counter reaches the threshold, it is moved to the LFU segment. The ghost queue is updated to reflect the object's continued relevance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    if obj.key in recently_accessed:
        recently_accessed[obj.key]['access_count'] += 1
        if recently_accessed[obj.key]['access_count'] >= SATURATE_THRESHOLD:
            lfu_segment[obj.key] = recently_accessed.pop(obj.key)
    elif obj.key in lfu_segment:
        lfu_segment[obj.key]['access_count'] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is placed in the 'recently accessed' segment with its saturate counter initialized. If the segment is full, the least recently accessed object is moved to the LFU segment or evicted if the LFU segment is also full. The ghost queue is updated with the evicted object's metadata.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    if len(recently_accessed) >= RECENTLY_ACCESSED_LIMIT:
        lru_key = min(recently_accessed, key=lambda k: recently_accessed[k]['access_count'])
        lfu_segment[lru_key] = recently_accessed.pop(lru_key)
    
    recently_accessed[obj.key] = {'access_count': 1}

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, its metadata (including access frequency) is added to the ghost queue. If the ghost queue is full, the oldest entry is removed. The saturate counters in the remaining segments are adjusted to ensure they reflect the current access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if len(ghost_queue) >= GHOST_QUEUE_LIMIT:
        ghost_queue.pop(0)
    
    if evicted_obj.key in recently_accessed:
        ghost_queue.append({'key': evicted_obj.key, 'access_count': recently_accessed[evicted_obj.key]['access_count']})
        del recently_accessed[evicted_obj.key]
    elif evicted_obj.key in lfu_segment:
        ghost_queue.append({'key': evicted_obj.key, 'access_count': lfu_segment[evicted_obj.key]['access_count']})
        del lfu_segment[evicted_obj.key]