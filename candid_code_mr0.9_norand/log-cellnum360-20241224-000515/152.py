# Import anything you need below
from collections import deque

# Put tunable constant parameters below
OVERFLOW_THRESHOLD = 1000  # Example threshold for overflow counter reset

# Put the metadata specifically maintained by the policy below. The policy maintains a circular queue to track cache entries, a timestamp for each entry to monitor temporal access patterns, and a counter for overflow handling to track how many times the queue has been cycled through.
circular_queue = deque()  # Circular queue to track cache entries
timestamps = {}  # Dictionary to track timestamps of each entry
overflow_counter = 0  # Counter for overflow handling
queue_pointer = 0  # Pointer to the current position in the circular queue

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the oldest entry in the circular queue that has the least recent timestamp, ensuring that both temporal locality and queue order are considered.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    oldest_time = float('inf')
    for key in circular_queue:
        if key in timestamps and timestamps[key] < oldest_time:
            oldest_time = timestamps[key]
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the timestamp of the accessed entry to the current time, ensuring that its temporal relevance is refreshed, and increments the overflow counter if the queue cycles through.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    timestamps[obj.key] = cache_snapshot.access_count
    if len(circular_queue) == cache_snapshot.capacity:
        global overflow_counter
        overflow_counter += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy places it at the current position in the circular queue, sets its timestamp to the current time, and increments the overflow counter if the queue cycles through.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    if len(circular_queue) < cache_snapshot.capacity:
        circular_queue.append(obj.key)
    else:
        circular_queue[queue_pointer] = obj.key
    
    timestamps[obj.key] = cache_snapshot.access_count
    if len(circular_queue) == cache_snapshot.capacity:
        global overflow_counter
        overflow_counter += 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy moves the circular queue pointer to the next position, resets the overflow counter if it reaches a predefined threshold, and updates the queue to reflect the removal.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    global queue_pointer, overflow_counter
    queue_pointer = (queue_pointer + 1) % cache_snapshot.capacity
    if overflow_counter >= OVERFLOW_THRESHOLD:
        overflow_counter = 0
    if evicted_obj.key in timestamps:
        del timestamps[evicted_obj.key]