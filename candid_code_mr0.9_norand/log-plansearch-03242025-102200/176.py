# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import defaultdict, deque

# Put tunable constant parameters below
SATURATE_COUNTER = 10

# Put the metadata specifically maintained by the policy below. The policy maintains a Count Bloom Filter to approximate access frequency, a ghost queue to track recently evicted objects, an LFU queue to manage in-cache objects based on frequency, and a saturate counter to limit the maximum frequency count.
count_bloom_filter = defaultdict(int)
lfu_queue = deque()
ghost_queue = deque()
ghost_queue_limit = 100  # Limit the size of the ghost queue

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the object with the lowest frequency count in the LFU queue. If there is a tie, it evicts the least recently used among them. The evicted object is then added to the ghost queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_freq = float('inf')
    for key in lfu_queue:
        if count_bloom_filter[key] < min_freq:
            min_freq = count_bloom_filter[key]
            candid_obj_key = key
        elif count_bloom_filter[key] == min_freq:
            candid_obj_key = key  # Evict the least recently used among ties
            break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the object's frequency count in the Count Bloom Filter and updates its position in the LFU queue. If the frequency count reaches the saturate counter limit, it stops increasing.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    if count_bloom_filter[obj.key] < SATURATE_COUNTER:
        count_bloom_filter[obj.key] += 1
    lfu_queue.remove(obj.key)
    lfu_queue.append(obj.key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its frequency count in the Count Bloom Filter, adds it to the LFU queue, and checks the ghost queue to see if the object was recently evicted. If found in the ghost queue, it gets a higher initial frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    if obj.key in ghost_queue:
        count_bloom_filter[obj.key] = 2  # Higher initial frequency if found in ghost queue
        ghost_queue.remove(obj.key)
    else:
        count_bloom_filter[obj.key] = 1
    lfu_queue.append(obj.key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy adds the object to the ghost queue and removes it from the LFU queue. The Count Bloom Filter is updated to reflect the removal, and the saturate counter remains unchanged.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if len(ghost_queue) >= ghost_queue_limit:
        ghost_queue.popleft()
    ghost_queue.append(evicted_obj.key)
    lfu_queue.remove(evicted_obj.key)
    del count_bloom_filter[evicted_obj.key]