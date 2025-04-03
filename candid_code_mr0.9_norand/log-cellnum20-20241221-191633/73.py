# Import anything you need below
from collections import defaultdict, deque

# Put tunable constant parameters below
BASE_FREQUENCY = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a dynamic frequency counter for each cache entry, a circular buffer index for tracking the order of entries, and an immediate eviction flag for entries that meet specific criteria.
frequency_counter = defaultdict(int)
circular_buffer = deque()
immediate_eviction_flags = defaultdict(bool)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first checking for any entries with the immediate eviction flag set. If none are found, it selects the entry with the lowest frequency counter, using the circular buffer index to break ties by evicting the oldest entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Check for immediate eviction flags
    for key in circular_buffer:
        if immediate_eviction_flags[key]:
            candid_obj_key = key
            break
    
    # If no immediate eviction flag is set, find the lowest frequency
    if candid_obj_key is None:
        min_frequency = float('inf')
        for key in circular_buffer:
            if frequency_counter[key] < min_frequency:
                min_frequency = frequency_counter[key]
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the frequency counter for the accessed entry is incremented, and the circular buffer index is updated to move the entry to the most recent position, while the immediate eviction flag is reset.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    frequency_counter[key] += 1
    if key in circular_buffer:
        circular_buffer.remove(key)
    circular_buffer.append(key)
    immediate_eviction_flags[key] = False

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its frequency counter to a base value, sets its position in the circular buffer to the most recent, and evaluates the immediate eviction criteria to set the flag if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    frequency_counter[key] = BASE_FREQUENCY
    circular_buffer.append(key)
    # Example criteria for immediate eviction flag (can be customized)
    immediate_eviction_flags[key] = (obj.size > cache_snapshot.capacity / 2)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy adjusts the circular buffer to close the gap left by the evicted entry, recalibrates the frequency counters of remaining entries incrementally to prevent overflow, and resets any immediate eviction flags as needed.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in circular_buffer:
        circular_buffer.remove(evicted_key)
    del frequency_counter[evicted_key]
    del immediate_eviction_flags[evicted_key]
    
    # Recalibrate frequency counters to prevent overflow
    for key in frequency_counter:
        frequency_counter[key] = max(BASE_FREQUENCY, frequency_counter[key] - 1)