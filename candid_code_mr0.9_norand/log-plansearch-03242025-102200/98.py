# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque
import time

# Put tunable constant parameters below
INITIAL_DECAY_VALUE = 10

# Put the metadata specifically maintained by the policy below. The policy maintains three segments: a FIFO queue for new objects, a decay counter for each object, and a main cache for frequently accessed objects. Each object has a timestamp and a decay value.
fifo_queue = deque()
main_cache = {}
decay_counter = {}
timestamps = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first checks the FIFO queue for eviction candidates. If the FIFO queue is empty, it looks for objects with the highest decay value in the main cache. If there are ties, it evicts the oldest object.
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
        max_decay = -1
        oldest_time = float('inf')
        for key, decay in decay_counter.items():
            if decay > max_decay or (decay == max_decay and timestamps[key] < oldest_time):
                max_decay = decay
                oldest_time = timestamps[key]
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the object's decay value is reset, and its timestamp is updated. If the object is in the FIFO queue, it is moved to the main cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    obj_key = obj.key
    decay_counter[obj_key] = INITIAL_DECAY_VALUE
    timestamps[obj_key] = cache_snapshot.access_count
    
    if obj_key in fifo_queue:
        fifo_queue.remove(obj_key)
        main_cache[obj_key] = obj

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is placed in the FIFO queue with an initial decay value and timestamp. The FIFO queue is checked for overflow, and if full, the oldest object is moved to the main cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    obj_key = obj.key
    decay_counter[obj_key] = INITIAL_DECAY_VALUE
    timestamps[obj_key] = cache_snapshot.access_count
    fifo_queue.append(obj_key)
    
    if cache_snapshot.size + obj.size > cache_snapshot.capacity:
        if len(fifo_queue) > 0:
            oldest_fifo_key = fifo_queue.popleft()
            main_cache[oldest_fifo_key] = cache_snapshot.cache[oldest_fifo_key]

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy updates the FIFO queue and main cache to ensure they are balanced. The decay values of all remaining objects are decremented periodically to prevent aging issues.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in decay_counter:
        del decay_counter[evicted_key]
    if evicted_key in timestamps:
        del timestamps[evicted_key]
    if evicted_key in main_cache:
        del main_cache[evicted_key]
    
    for key in decay_counter:
        decay_counter[key] -= 1