# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, defaultdict

# Put tunable constant parameters below
CLOCK_BUFFER_SIZE = 100  # Example size, can be tuned

# Put the metadata specifically maintained by the policy below. The policy maintains a circular buffer (clock) for cache entries, a ghost queue for recently evicted items, and an LFU queue to track access frequencies. Each cache entry has a reference bit and a frequency counter.
clock_buffer = deque(maxlen=CLOCK_BUFFER_SIZE)
ghost_queue = deque(maxlen=CLOCK_BUFFER_SIZE)
lfu_queue = defaultdict(int)
reference_bits = {}
frequency_counters = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy traverses the clock buffer to find the first entry with a reference bit of 0. If found, it is evicted. If all entries have a reference bit of 1, it resets the bits and increments the frequency counters, then retries. The evicted entry is added to the ghost queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    while True:
        for key in clock_buffer:
            if reference_bits[key] == 0:
                candid_obj_key = key
                break
            else:
                reference_bits[key] = 0
        if candid_obj_key is not None:
            break
        # If all reference bits were 1, reset them and increment frequency counters
        for key in clock_buffer:
            reference_bits[key] = 0
            frequency_counters[key] += 1

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    On a cache hit, the reference bit of the entry is set to 1, and its frequency counter is incremented. The LFU queue is updated to reflect the new frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    reference_bits[key] = 1
    frequency_counters[key] += 1
    lfu_queue[key] = frequency_counters[key]

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    On inserting a new object, the object is placed in the clock buffer with a reference bit of 1 and a frequency counter of 1. The LFU queue is updated to include the new object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    clock_buffer.append(key)
    reference_bits[key] = 1
    frequency_counters[key] = 1
    lfu_queue[key] = 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the evicted object's metadata is added to the ghost queue with its frequency counter. The clock buffer is updated to remove the evicted entry, and the LFU queue is updated to remove the evicted entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    ghost_queue.append((evicted_key, frequency_counters[evicted_key]))
    clock_buffer.remove(evicted_key)
    del reference_bits[evicted_key]
    del frequency_counters[evicted_key]
    del lfu_queue[evicted_key]