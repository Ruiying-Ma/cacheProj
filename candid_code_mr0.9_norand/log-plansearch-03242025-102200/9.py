# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import defaultdict, deque

# Put tunable constant parameters below

# Put the metadata specifically maintained by the policy below. The policy maintains two queues: an LFU queue to track the frequency of access for each object, and an LRU queue to track the recency of access. Each object in the cache has a frequency counter and a timestamp.
lfu_queue = defaultdict(int)  # key -> frequency
lru_queue = deque()  # list of keys in LRU order

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first identifying the object with the lowest frequency in the LFU queue. If there are multiple objects with the same lowest frequency, it then selects the least recently used object among them using the LRU queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_freq = float('inf')
    for key in cache_snapshot.cache:
        if lfu_queue[key] < min_freq:
            min_freq = lfu_queue[key]
    
    candidates = [key for key in lru_queue if lfu_queue[key] == min_freq]
    if candidates:
        candid_obj_key = candidates[0]
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the frequency counter of the accessed object in the LFU queue and updates its position in the LRU queue to reflect the most recent access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    lfu_queue[obj.key] += 1
    if obj.key in lru_queue:
        lru_queue.remove(obj.key)
    lru_queue.appendleft(obj.key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its frequency counter to 1 in the LFU queue and adds it to the front of the LRU queue to mark it as the most recently used.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    lfu_queue[obj.key] = 1
    lru_queue.appendleft(obj.key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy removes the object from both the LFU and LRU queues and adjusts the positions of the remaining objects if necessary to maintain the correct order.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in lfu_queue:
        del lfu_queue[evicted_obj.key]
    if evicted_obj.key in lru_queue:
        lru_queue.remove(evicted_obj.key)