# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque

# Put tunable constant parameters below
HIT_RATE_THRESHOLD = 0.8  # Threshold to increment dynamic capacity counter

# Put the metadata specifically maintained by the policy below. The policy maintains a timestamp for each cache entry, a queue to track the order of access, and a dynamic capacity counter that adjusts based on access patterns.
timestamps = {}
access_queue = deque()
dynamic_capacity_counter = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on the oldest timestamp in the queue, but also considers the dynamic capacity counter to decide if multiple evictions are needed to adjust the cache size.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    global dynamic_capacity_counter
    candid_obj_key = None
    # Your code below
    while cache_snapshot.size + obj.size > cache_snapshot.capacity - dynamic_capacity_counter:
        if access_queue:
            oldest_key = access_queue.popleft()
            if oldest_key in cache_snapshot.cache:
                candid_obj_key = oldest_key
                break
        else:
            break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the timestamp of the accessed entry to the current time and promotes the entry to the front of the queue, while also incrementing the dynamic capacity counter if the hit rate is high.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    global dynamic_capacity_counter
    # Your code below
    current_time = cache_snapshot.access_count
    timestamps[obj.key] = current_time
    if obj.key in access_queue:
        access_queue.remove(obj.key)
    access_queue.appendleft(obj.key)
    
    hit_rate = cache_snapshot.hit_count / (cache_snapshot.hit_count + cache_snapshot.miss_count)
    if hit_rate > HIT_RATE_THRESHOLD:
        dynamic_capacity_counter += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns the current timestamp to the new entry, places it at the front of the queue, and adjusts the dynamic capacity counter to ensure the cache size remains optimal.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    global dynamic_capacity_counter
    # Your code below
    current_time = cache_snapshot.access_count
    timestamps[obj.key] = current_time
    access_queue.appendleft(obj.key)
    
    # Adjust dynamic capacity counter if needed
    if cache_snapshot.size > cache_snapshot.capacity:
        dynamic_capacity_counter = max(0, dynamic_capacity_counter - 1)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes the oldest entry from the queue, updates the dynamic capacity counter to reflect the new cache size, and recalculates the optimal capacity based on recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    global dynamic_capacity_counter
    # Your code below
    if evicted_obj.key in timestamps:
        del timestamps[evicted_obj.key]
    if evicted_obj.key in access_queue:
        access_queue.remove(evicted_obj.key)
    
    # Recalculate dynamic capacity counter
    if cache_snapshot.size < cache_snapshot.capacity:
        dynamic_capacity_counter = max(0, dynamic_capacity_counter - 1)