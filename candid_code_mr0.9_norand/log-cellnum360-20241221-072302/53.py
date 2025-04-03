# Import anything you need below
from collections import deque, defaultdict

# Put tunable constant parameters below

# Put the metadata specifically maintained by the policy below. The policy maintains a circular buffer to track cache entries, a frequency counter for each entry to record access frequency, and a rotational index to manage the order of entries. Each entry also has a timestamp for instant access updates.
circular_buffer = deque()  # Circular buffer to track cache entries
frequency_counter = defaultdict(int)  # Frequency counter for each entry
timestamps = {}  # Timestamps for each entry
rotational_index = 0  # Rotational index to manage order of entries

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest frequency count. In case of a tie, it selects the oldest entry based on the rotational order in the circular buffer.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_frequency = float('inf')
    oldest_timestamp = float('inf')

    for key in circular_buffer:
        freq = frequency_counter[key]
        timestamp = timestamps[key]
        if freq < min_frequency or (freq == min_frequency and timestamp < oldest_timestamp):
            min_frequency = freq
            oldest_timestamp = timestamp
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the frequency counter for the accessed entry is incremented, and its timestamp is updated to the current time to reflect instant access. The rotational index is adjusted to move the entry to the end of the buffer.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    frequency_counter[key] += 1
    timestamps[key] = cache_snapshot.access_count

    # Move the entry to the end of the circular buffer
    circular_buffer.remove(key)
    circular_buffer.append(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its frequency counter to one, sets its timestamp to the current time, and places it at the end of the circular buffer, updating the rotational index accordingly.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    frequency_counter[key] = 1
    timestamps[key] = cache_snapshot.access_count
    circular_buffer.append(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes the entry from the circular buffer, decrements the rotational index for subsequent entries, and resets the frequency counter and timestamp for the evicted entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    circular_buffer.remove(evicted_key)
    del frequency_counter[evicted_key]
    del timestamps[evicted_key]