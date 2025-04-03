# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import defaultdict, deque

# Put tunable constant parameters below
SATURATE_COUNTER_LIMIT = 10
GHOST_QUEUE_LIMIT = 100

# Put the metadata specifically maintained by the policy below. The policy maintains three main data structures: an LFU queue to track the frequency of accesses, an LRU queue to track the recency of accesses, and a ghost queue to record recently evicted objects. Additionally, each object has a saturate counter to limit the maximum frequency count.
lfu_queue = defaultdict(int)  # key -> frequency count
lru_queue = deque()  # list of keys in LRU order
ghost_queue = deque()  # list of keys in ghost queue

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first checking the LFU queue for the least frequently used object. If there are ties, it then checks the LRU queue to find the least recently used among them. The evicted object is then added to the ghost queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_freq = min(lfu_queue.values())
    candidates = [key for key, freq in lfu_queue.items() if freq == min_freq]
    
    for key in lru_queue:
        if key in candidates:
            candid_obj_key = key
            break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the object's frequency count in the LFU queue is incremented, respecting the saturate counter limit. The object's position in the LRU queue is updated to reflect its recent access. If the object was in the ghost queue, it is removed from there.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    if lfu_queue[key] < SATURATE_COUNTER_LIMIT:
        lfu_queue[key] += 1
    
    if key in lru_queue:
        lru_queue.remove(key)
    lru_queue.appendleft(key)
    
    if key in ghost_queue:
        ghost_queue.remove(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is added to both the LFU and LRU queues with an initial frequency count of 1. The ghost queue is checked to see if the object was recently evicted, and if so, it is removed from the ghost queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    lfu_queue[key] = 1
    lru_queue.appendleft(key)
    
    if key in ghost_queue:
        ghost_queue.remove(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, it is added to the ghost queue. The LFU and LRU queues are updated to remove the evicted object. The ghost queue may also be pruned to maintain a manageable size, ensuring it only keeps track of the most recently evicted objects.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    ghost_queue.appendleft(evicted_key)
    
    if len(ghost_queue) > GHOST_QUEUE_LIMIT:
        ghost_queue.pop()
    
    if evicted_key in lfu_queue:
        del lfu_queue[evicted_key]
    
    if evicted_key in lru_queue:
        lru_queue.remove(evicted_key)