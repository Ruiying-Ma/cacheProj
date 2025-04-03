# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, defaultdict

# Put tunable constant parameters below
FIFO_QUEUE_SIZE = 10  # Example size, can be tuned
GHOST_QUEUE_SIZE = 10  # Example size, can be tuned
FREQUENCY_THRESHOLD = 3  # Example threshold, can be tuned

# Put the metadata specifically maintained by the policy below. The policy maintains a segmented cache with three segments: a FIFO queue for new objects, an LFU queue for frequently accessed objects, and a ghost queue for recently evicted objects. Each object in the cache has a frequency counter.
fifo_queue = deque()
lfu_queue = defaultdict(int)
ghost_queue = deque()
frequency_counter = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first checks the FIFO queue for eviction candidates. If the FIFO queue is empty, it checks the LFU queue for the least frequently used object. If both queues are empty, it evicts the oldest object in the ghost queue.
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
        candid_obj_key = min(lfu_queue, key=lfu_queue.get)
    elif ghost_queue:
        candid_obj_key = ghost_queue.popleft()
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the object's frequency counter is incremented. If the object is in the FIFO queue and its frequency exceeds a threshold, it is moved to the LFU queue. The ghost queue is not updated on a hit.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    frequency_counter[obj.key] += 1
    if obj.key in fifo_queue and frequency_counter[obj.key] > FREQUENCY_THRESHOLD:
        fifo_queue.remove(obj.key)
        lfu_queue[obj.key] = frequency_counter[obj.key]

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    When a new object is inserted, it is placed in the FIFO queue with a frequency counter set to 1. If the FIFO queue is full, the oldest object is evicted to make space. The ghost queue is updated to include the evicted object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    if len(fifo_queue) >= FIFO_QUEUE_SIZE:
        evicted_key = fifo_queue.popleft()
        ghost_queue.append(evicted_key)
        if len(ghost_queue) > GHOST_QUEUE_SIZE:
            ghost_queue.popleft()
    
    fifo_queue.append(obj.key)
    frequency_counter[obj.key] = 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the evicted object is added to the ghost queue. If the ghost queue exceeds its size limit, the oldest object in the ghost queue is removed. The FIFO and LFU queues are updated to reflect the current state of the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    ghost_queue.append(evicted_obj.key)
    if len(ghost_queue) > GHOST_QUEUE_SIZE:
        ghost_queue.popleft()
    
    if evicted_obj.key in fifo_queue:
        fifo_queue.remove(evicted_obj.key)
    if evicted_obj.key in lfu_queue:
        del lfu_queue[evicted_obj.key]
    if evicted_obj.key in frequency_counter:
        del frequency_counter[evicted_obj.key]