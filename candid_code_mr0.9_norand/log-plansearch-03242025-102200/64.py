# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, defaultdict

# Put tunable constant parameters below
CLOCK_SIZE = 1000  # Example size, can be tuned

# Put the metadata specifically maintained by the policy below. The policy maintains a circular list of cache frames (Clock), a Count Bloom Filter to approximate access frequencies, and an LFU queue to track the least-frequently-used objects.
clock_hand = 0
clock_list = [None] * CLOCK_SIZE
count_bloom_filter = defaultdict(int)
lfu_queue = deque()

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy traverses the Clock list to find a candidate for eviction. It uses the Count Bloom Filter to check the access frequency of each candidate. If the candidate is among the least-frequently-used objects in the LFU queue, it is chosen for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    global clock_hand
    candid_obj_key = None
    # Your code below
    while True:
        candidate = clock_list[clock_hand]
        if candidate is not None and candidate.key in cache_snapshot.cache:
            if count_bloom_filter[candidate.key] == min(count_bloom_filter.values()):
                candid_obj_key = candidate.key
                break
        clock_hand = (clock_hand + 1) % CLOCK_SIZE
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the access count in the Count Bloom Filter for the accessed object and updates its position in the LFU queue to reflect its increased frequency. The Clock hand remains unchanged.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    count_bloom_filter[obj.key] += 1
    if obj.key in lfu_queue:
        lfu_queue.remove(obj.key)
    lfu_queue.append(obj.key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access count in the Count Bloom Filter, adds it to the LFU queue, and advances the Clock hand to the next position.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    global clock_hand
    # Your code below
    count_bloom_filter[obj.key] = 1
    lfu_queue.append(obj.key)
    clock_list[clock_hand] = obj
    clock_hand = (clock_hand + 1) % CLOCK_SIZE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy removes its entry from the Count Bloom Filter and the LFU queue. The Clock hand is then advanced to the next position to prepare for the next potential eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    global clock_hand
    # Your code below
    if evicted_obj.key in count_bloom_filter:
        del count_bloom_filter[evicted_obj.key]
    if evicted_obj.key in lfu_queue:
        lfu_queue.remove(evicted_obj.key)
    clock_hand = (clock_hand + 1) % CLOCK_SIZE