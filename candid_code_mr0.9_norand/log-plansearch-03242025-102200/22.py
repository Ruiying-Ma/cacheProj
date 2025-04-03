# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, defaultdict

# Put tunable constant parameters below
SATURATE_LIMIT = 10

# Put the metadata specifically maintained by the policy below. The policy maintains an LRU queue to track the order of access and a saturate counter for each cache entry to count the number of accesses up to a predefined limit.
lru_queue = deque()
saturate_counter = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the least-recently-used entry from the LRU queue that has the lowest saturate counter value. If there is a tie, the oldest entry in the LRU queue is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_saturate_value = float('inf')
    for key in lru_queue:
        if saturate_counter[key] < min_saturate_value:
            min_saturate_value = saturate_counter[key]
            candid_obj_key = key
        elif saturate_counter[key] == min_saturate_value:
            if lru_queue.index(key) < lru_queue.index(candid_obj_key):
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the accessed entry is moved to the front of the LRU queue, and its saturate counter is incremented by one, stopping at the predefined upper limit.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    if obj.key in lru_queue:
        lru_queue.remove(obj.key)
    lru_queue.appendleft(obj.key)
    if saturate_counter[obj.key] < SATURATE_LIMIT:
        saturate_counter[obj.key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the object is added to the front of the LRU queue with its saturate counter initialized to one.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    lru_queue.appendleft(obj.key)
    saturate_counter[obj.key] = 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the entry is removed from the LRU queue, and its saturate counter is reset. No further updates are needed for the remaining metadata.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in lru_queue:
        lru_queue.remove(evicted_obj.key)
    if evicted_obj.key in saturate_counter:
        del saturate_counter[evicted_obj.key]