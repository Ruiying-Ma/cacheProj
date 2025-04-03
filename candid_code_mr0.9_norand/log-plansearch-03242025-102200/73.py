# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

from collections import deque, defaultdict

# Put tunable constant parameters below
FIFO_QUEUE_SIZE_LIMIT = 10  # Example size limit for FIFO queue

# Put the metadata specifically maintained by the policy below. The policy maintains three segments: a FIFO queue for newly inserted objects, an LRU queue for recently accessed objects, and a counter for tracking the number of accesses to each object.
fifo_queue = deque()
lru_queue = deque()
access_counter = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first checks the FIFO queue for eviction candidates. If the FIFO queue is empty, it then checks the LRU queue. The object at the front of the FIFO queue is evicted first, followed by the least recently used object in the LRU queue if necessary.
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
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the accessed object is moved to the LRU queue if it is not already there. The access counter for the object is incremented. If the object is already in the LRU queue, it is moved to the back of the queue to mark it as recently used.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    access_counter[obj.key] += 1
    if obj.key in fifo_queue:
        fifo_queue.remove(obj.key)
        lru_queue.append(obj.key)
    elif obj.key in lru_queue:
        lru_queue.remove(obj.key)
        lru_queue.append(obj.key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    When a new object is inserted, it is added to the FIFO queue and its access counter is initialized to 1. If the FIFO queue exceeds its size limit, the oldest object is moved to the LRU queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    fifo_queue.append(obj.key)
    access_counter[obj.key] = 1
    if len(fifo_queue) > FIFO_QUEUE_SIZE_LIMIT:
        oldest_key = fifo_queue.popleft()
        lru_queue.append(oldest_key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy checks the FIFO and LRU queues to ensure they are within their size limits. If the FIFO queue is empty, the oldest object from the LRU queue is moved to the FIFO queue to maintain balance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in fifo_queue:
        fifo_queue.remove(evicted_obj.key)
    elif evicted_obj.key in lru_queue:
        lru_queue.remove(evicted_obj.key)
    
    if not fifo_queue and lru_queue:
        oldest_key = lru_queue.popleft()
        fifo_queue.append(oldest_key)