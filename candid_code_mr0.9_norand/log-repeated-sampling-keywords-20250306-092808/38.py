# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import defaultdict, deque

# Put tunable constant parameters below
LATENCY_THRESHOLD = 10  # Example threshold, can be tuned

# Put the metadata specifically maintained by the policy below. The policy maintains latency tracking for each object, a frequency counter, a queue for balancing, and an adaptive threshold for eviction decisions.
frequency_counter = defaultdict(int)
latency_tracker = {}
eviction_queue = deque()
adaptive_threshold = LATENCY_THRESHOLD

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first identifying objects with latency above the adaptive threshold, then among those, it selects the one with the lowest frequency. If no objects exceed the latency threshold, it evicts the least frequently accessed object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    candidates = [key for key, latency in latency_tracker.items() if latency > adaptive_threshold]
    
    if candidates:
        # Evict the one with the lowest frequency among those with latency above the threshold
        candid_obj_key = min(candidates, key=lambda k: frequency_counter[k])
    else:
        # Evict the least frequently accessed object
        candid_obj_key = min(cache_snapshot.cache.keys(), key=lambda k: frequency_counter[k])
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy increments the frequency counter for the accessed object, updates its latency tracking based on the current access time, and rebalances the queue to reflect the updated frequency and latency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    frequency_counter[obj.key] += 1
    latency_tracker[obj.key] = cache_snapshot.access_count
    # Rebalance the queue
    eviction_queue.remove(obj.key)
    eviction_queue.append(obj.key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its frequency counter to 1, sets its initial latency based on the insertion time, and places it in the appropriate position in the queue based on its latency and frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    frequency_counter[obj.key] = 1
    latency_tracker[obj.key] = cache_snapshot.access_count
    eviction_queue.append(obj.key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy recalculates the adaptive threshold based on the remaining objects' latencies, adjusts the queue to remove the evicted object, and updates any related metadata to maintain consistency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    del frequency_counter[evicted_obj.key]
    del latency_tracker[evicted_obj.key]
    eviction_queue.remove(evicted_obj.key)
    
    # Recalculate the adaptive threshold
    if latency_tracker:
        adaptive_threshold = sum(latency_tracker.values()) / len(latency_tracker)
    else:
        adaptive_threshold = LATENCY_THRESHOLD