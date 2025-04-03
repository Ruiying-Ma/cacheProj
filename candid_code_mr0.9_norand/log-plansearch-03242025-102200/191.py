# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, defaultdict

# Put tunable constant parameters below
CLOCK_POINTER = 0

# Put the metadata specifically maintained by the policy below. The policy maintains a circular buffer (Clock) for cyclic traversal, a Count Bloom Filter to approximate access frequency, a FIFO queue to track insertion order, and an LRU queue to track recent usage.
clock_buffer = []
count_bloom_filter = defaultdict(int)
fifo_queue = deque()
lru_queue = deque()

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first checks the Clock pointer for eviction candidates. If the candidate's access frequency (from the Count Bloom Filter) is low, it is chosen for eviction. If not, the Clock pointer moves to the next candidate. This process repeats until a suitable candidate is found.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    global CLOCK_POINTER
    while True:
        candidate_key = clock_buffer[CLOCK_POINTER]
        if count_bloom_filter[candidate_key] <= 1:
            candid_obj_key = candidate_key
            break
        else:
            count_bloom_filter[candidate_key] -= 1
            CLOCK_POINTER = (CLOCK_POINTER + 1) % len(clock_buffer)
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Count Bloom Filter is updated to increase the access frequency of the object. The object is also moved to the front of the LRU queue to mark it as recently used. The FIFO queue remains unchanged.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    count_bloom_filter[obj.key] += 1
    if obj.key in lru_queue:
        lru_queue.remove(obj.key)
    lru_queue.appendleft(obj.key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is added to the Clock buffer, the Count Bloom Filter is initialized for the object, it is placed at the end of the FIFO queue, and added to the front of the LRU queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    clock_buffer.append(obj.key)
    count_bloom_filter[obj.key] = 1
    fifo_queue.append(obj.key)
    lru_queue.appendleft(obj.key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the object is removed from the Clock buffer, its entry in the Count Bloom Filter is cleared, it is removed from the FIFO queue, and it is also removed from the LRU queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    clock_buffer.remove(evicted_obj.key)
    del count_bloom_filter[evicted_obj.key]
    fifo_queue.remove(evicted_obj.key)
    lru_queue.remove(evicted_obj.key)