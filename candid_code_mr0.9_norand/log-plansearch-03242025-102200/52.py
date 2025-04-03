# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, defaultdict

# Put tunable constant parameters below
FIFO_THRESHOLD = 5  # Threshold for moving objects from FIFO to LFU

# Put the metadata specifically maintained by the policy below. The policy maintains three segments: a FIFO queue for newly inserted objects, an LFU queue for frequently accessed objects, and a counter for each object to track access frequency.
fifo_queue = deque()
lfu_queue = []
access_counter = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first checks the FIFO queue for eviction candidates. If the FIFO queue is empty, it then checks the LFU queue and evicts the least frequently used object.
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
    else:
        lfu_queue.sort(key=lambda x: access_counter[x])
        candid_obj_key = lfu_queue.pop(0)
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access counter for the object is incremented. If the object is in the FIFO queue and its access count exceeds a threshold, it is moved to the LFU queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    access_counter[obj.key] += 1
    if obj.key in fifo_queue and access_counter[obj.key] > FIFO_THRESHOLD:
        fifo_queue.remove(obj.key)
        lfu_queue.append(obj.key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    When a new object is inserted, it is placed in the FIFO queue and its access counter is initialized to 1. If the FIFO queue is full, the oldest object is moved to the LFU queue before the new object is inserted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    access_counter[obj.key] = 1
    if len(fifo_queue) >= FIFO_THRESHOLD:
        oldest_obj_key = fifo_queue.popleft()
        lfu_queue.append(oldest_obj_key)
    fifo_queue.append(obj.key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the metadata for the evicted object is removed. If the eviction was from the FIFO queue, the next oldest object remains in place. If from the LFU queue, the LFU queue is re-evaluated to ensure the least frequently used object is correctly identified.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in fifo_queue:
        fifo_queue.remove(evicted_obj.key)
    if evicted_obj.key in lfu_queue:
        lfu_queue.remove(evicted_obj.key)
    del access_counter[evicted_obj.key]