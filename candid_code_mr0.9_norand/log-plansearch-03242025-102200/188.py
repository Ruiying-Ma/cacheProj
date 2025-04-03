# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, defaultdict

# Put tunable constant parameters below
SATURATE_LIMIT = 5
FIFO_QUEUE_LIMIT = 10

# Put the metadata specifically maintained by the policy below. The policy maintains three segments: a FIFO queue for newly inserted objects, an LRU queue for frequently accessed objects, and a saturate counter for each object to track access frequency up to a predefined limit.
fifo_queue = deque()
lru_queue = deque()
saturate_counter = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first checks the FIFO queue for eviction candidates, prioritizing the oldest object. If the FIFO queue is empty, it then checks the LRU queue, evicting the least recently used object. If both queues are empty, it evicts the object with the lowest saturate counter value.
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
        candid_obj_key = lru_queue.pop()
    else:
        # Find the object with the lowest saturate counter value
        min_saturate_value = min(saturate_counter.values())
        for key, value in saturate_counter.items():
            if value == min_saturate_value:
                candid_obj_key = key
                break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the object's saturate counter is incremented if it hasn't reached the upper limit. The object is moved to the front of the LRU queue if it is not already there, ensuring it is marked as recently used.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    if saturate_counter[obj.key] < SATURATE_LIMIT:
        saturate_counter[obj.key] += 1
    
    if obj.key in lru_queue:
        lru_queue.remove(obj.key)
    lru_queue.appendleft(obj.key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is placed at the end of the FIFO queue. If the FIFO queue exceeds its size limit, the oldest object is moved to the LRU queue. The saturate counter for the new object is initialized to 1.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    fifo_queue.append(obj.key)
    saturate_counter[obj.key] = 1
    
    if len(fifo_queue) > FIFO_QUEUE_LIMIT:
        oldest_obj_key = fifo_queue.popleft()
        lru_queue.appendleft(oldest_obj_key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy checks if the FIFO or LRU queue needs rebalancing. If an object was evicted from the FIFO queue, the next oldest object is moved to the LRU queue. The saturate counter for the evicted object is removed from memory.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in fifo_queue:
        fifo_queue.remove(evicted_obj.key)
        if fifo_queue:
            oldest_obj_key = fifo_queue.popleft()
            lru_queue.appendleft(oldest_obj_key)
    elif evicted_obj.key in lru_queue:
        lru_queue.remove(evicted_obj.key)
    
    del saturate_counter[evicted_obj.key]