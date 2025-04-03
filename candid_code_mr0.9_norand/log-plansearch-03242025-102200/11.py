# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, defaultdict

# Put tunable constant parameters below
RECENTLY_ACCESSED_LIMIT = 10  # Maximum number of objects in the recently accessed segment

# Put the metadata specifically maintained by the policy below. The policy maintains three segments: a 'recently accessed' segment for objects accessed only once, a 'frequently accessed' segment for objects accessed more than once, and an LFU queue within the 'frequently accessed' segment to track the frequency of accesses.
recently_accessed = deque()  # Stores keys of recently accessed objects
frequently_accessed = {}  # Stores objects in the frequently accessed segment
lfu_queue = defaultdict(int)  # Frequency count of objects in the frequently accessed segment

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first evicts objects from the 'recently accessed' segment if it is not empty. If the 'recently accessed' segment is empty, it evicts the least-frequently-used object from the LFU queue in the 'frequently accessed' segment.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    if recently_accessed:
        candid_obj_key = recently_accessed.popleft()
    else:
        # Find the least frequently used object in the frequently accessed segment
        if lfu_queue:
            candid_obj_key = min(lfu_queue, key=lfu_queue.get)
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, if the object is in the 'recently accessed' segment, it is moved to the 'frequently accessed' segment and its frequency count is initialized. If the object is already in the 'frequently accessed' segment, its frequency count in the LFU queue is incremented.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    if obj.key in recently_accessed:
        recently_accessed.remove(obj.key)
        frequently_accessed[obj.key] = obj
        lfu_queue[obj.key] = 1
    elif obj.key in frequently_accessed:
        lfu_queue[obj.key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is placed in the 'recently accessed' segment. If the 'recently accessed' segment is full, the least recently accessed object in this segment is moved to the 'frequently accessed' segment with its frequency count initialized.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    if len(recently_accessed) >= RECENTLY_ACCESSED_LIMIT:
        moved_obj_key = recently_accessed.popleft()
        moved_obj = cache_snapshot.cache[moved_obj_key]
        frequently_accessed[moved_obj_key] = moved_obj
        lfu_queue[moved_obj_key] = 1
    recently_accessed.append(obj.key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy checks if the 'recently accessed' segment has space and moves objects from the 'frequently accessed' segment if necessary. The LFU queue is updated to remove the evicted object and adjust the frequency counts accordingly.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in recently_accessed:
        recently_accessed.remove(evicted_obj.key)
    elif evicted_obj.key in frequently_accessed:
        del frequently_accessed[evicted_obj.key]
        del lfu_queue[evicted_obj.key]
    
    # Check if we need to move objects from frequently accessed to recently accessed
    while len(recently_accessed) < RECENTLY_ACCESSED_LIMIT and frequently_accessed:
        # Move the least frequently used object from frequently accessed to recently accessed
        lfu_key = min(lfu_queue, key=lfu_queue.get)
        recently_accessed.append(lfu_key)
        del frequently_accessed[lfu_key]
        del lfu_queue[lfu_key]