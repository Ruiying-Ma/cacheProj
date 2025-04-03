# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

from collections import deque

# Put tunable constant parameters below
FIFO_QUEUE_SIZE_LIMIT = 100  # Example size limit for FIFO queue
GHOST_QUEUE_SIZE_LIMIT = 100  # Example size limit for Ghost queue

# Put the metadata specifically maintained by the policy below. The policy maintains four main data structures: a FIFO queue for newly inserted objects, an LRU queue for frequently accessed objects, a ghost queue for recently evicted objects, and a segmentation flag for each object to indicate if it has been accessed more than once.

fifo_queue = deque()
lru_queue = deque()
ghost_queue = deque()
segmentation_flag = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first checks the FIFO queue for eviction candidates. If the FIFO queue is empty, it then checks the LRU queue. If both are empty, it evicts the least recently used object from the ghost queue.
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
    elif lru_queue:
        candid_obj_key = lru_queue.popleft()
    elif ghost_queue:
        candid_obj_key = ghost_queue.popleft()
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy checks the segmentation flag of the object. If the object is in the FIFO queue and has been accessed more than once, it is moved to the LRU queue. The LRU queue is then updated to reflect the recent access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    if key in fifo_queue and segmentation_flag[key] > 1:
        fifo_queue.remove(key)
        lru_queue.append(key)
    elif key in lru_queue:
        lru_queue.remove(key)
        lru_queue.append(key)
    segmentation_flag[key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy places it in the FIFO queue and sets its segmentation flag to indicate it has been accessed once. If the FIFO queue exceeds its size limit, the oldest object is moved to the ghost queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    fifo_queue.append(key)
    segmentation_flag[key] = 1
    if len(fifo_queue) > FIFO_QUEUE_SIZE_LIMIT:
        oldest_key = fifo_queue.popleft()
        ghost_queue.append(oldest_key)
        if len(ghost_queue) > GHOST_QUEUE_SIZE_LIMIT:
            ghost_queue.popleft()

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy updates the ghost queue to include the evicted object. If the ghost queue exceeds its size limit, the oldest object in the ghost queue is discarded.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    ghost_queue.append(evicted_key)
    if len(ghost_queue) > GHOST_QUEUE_SIZE_LIMIT:
        ghost_queue.popleft()
    if evicted_key in segmentation_flag:
        del segmentation_flag[evicted_key]