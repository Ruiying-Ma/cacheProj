# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, defaultdict

# Put tunable constant parameters below
FIFO_SIZE_LIMIT = 10
LFU_SIZE_LIMIT = 10

# Put the metadata specifically maintained by the policy below. The policy maintains three segments: FIFO, LFU, and LRU. Each segment has its own queue to track objects. Additionally, a global counter tracks the total number of accesses for LFU, and a timestamp is used for LRU.
fifo_queue = deque()
lfu_queue = deque()
lru_queue = deque()
lfu_access_count = defaultdict(int)
lru_timestamps = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first checks the FIFO segment for eviction candidates. If the FIFO segment is empty, it checks the LFU segment, evicting the least frequently used object. If both FIFO and LFU segments are empty, it evicts the least recently used object from the LRU segment.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    if fifo_queue:
        candid_obj_key = fifo_queue.popleft()
    elif lfu_queue:
        candid_obj_key = min(lfu_queue, key=lambda k: lfu_access_count[k])
        lfu_queue.remove(candid_obj_key)
    elif lru_queue:
        candid_obj_key = min(lru_queue, key=lambda k: lru_timestamps[k])
        lru_queue.remove(candid_obj_key)
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the object is moved to the LRU segment if it is not already there. The access counter for the LFU segment is incremented. The timestamp for the LRU segment is updated to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    obj_key = obj.key
    if obj_key in fifo_queue:
        fifo_queue.remove(obj_key)
    elif obj_key in lfu_queue:
        lfu_queue.remove(obj_key)
        lfu_access_count[obj_key] += 1
    if obj_key not in lru_queue:
        lru_queue.append(obj_key)
    lru_timestamps[obj_key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    Upon inserting a new object, it is placed in the FIFO segment. If the FIFO segment exceeds its size limit, the oldest object is moved to the LFU segment. If the LFU segment exceeds its size limit, the least frequently used object is moved to the LRU segment.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    obj_key = obj.key
    fifo_queue.append(obj_key)
    if len(fifo_queue) > FIFO_SIZE_LIMIT:
        moved_obj_key = fifo_queue.popleft()
        lfu_queue.append(moved_obj_key)
        lfu_access_count[moved_obj_key] = 1
    if len(lfu_queue) > LFU_SIZE_LIMIT:
        moved_obj_key = min(lfu_queue, key=lambda k: lfu_access_count[k])
        lfu_queue.remove(moved_obj_key)
        lru_queue.append(moved_obj_key)
        lru_timestamps[moved_obj_key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the metadata of the segment from which the object was evicted is updated. If from FIFO, the oldest object is removed. If from LFU, the access counter is decremented. If from LRU, the timestamp is cleared.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in fifo_queue:
        fifo_queue.remove(evicted_key)
    elif evicted_key in lfu_queue:
        lfu_queue.remove(evicted_key)
        del lfu_access_count[evicted_key]
    elif evicted_key in lru_queue:
        lru_queue.remove(evicted_key)
        del lru_timestamps[evicted_key]