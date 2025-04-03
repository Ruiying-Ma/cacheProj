# Import anything you need below
from collections import deque, defaultdict

# Put tunable constant parameters below
INITIAL_DYNAMIC_THRESHOLD = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a cyclic buffer to track cache entries, a frequency counter for each entry to record access frequency, and a timestamp of the last access. It also keeps a dynamic frequency threshold that adjusts based on overall cache access patterns.
cyclic_buffer = deque()
frequency_counter = defaultdict(int)
last_access_timestamp = {}
dynamic_frequency_threshold = INITIAL_DYNAMIC_THRESHOLD

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying entries with a frequency below the dynamic threshold and the oldest timestamp. If no entries meet these criteria, it defaults to the least frequently used entry in the cyclic buffer.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    oldest_timestamp = float('inf')
    for key in cyclic_buffer:
        if frequency_counter[key] < dynamic_frequency_threshold:
            if last_access_timestamp[key] < oldest_timestamp:
                oldest_timestamp = last_access_timestamp[key]
                candid_obj_key = key

    if candid_obj_key is None:
        # Default to the least frequently used entry in the cyclic buffer
        min_frequency = float('inf')
        for key in cyclic_buffer:
            if frequency_counter[key] < min_frequency:
                min_frequency = frequency_counter[key]
                candid_obj_key = key

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the frequency counter for the accessed entry is incremented, and its timestamp is updated to the current time. The dynamic frequency threshold is recalibrated based on the updated access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    frequency_counter[obj.key] += 1
    last_access_timestamp[obj.key] = cache_snapshot.access_count
    # Recalibrate dynamic frequency threshold
    dynamic_frequency_threshold = max(1, sum(frequency_counter.values()) // len(frequency_counter))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its frequency counter to one and sets its timestamp to the current time. The cyclic buffer is updated to include the new entry, and the dynamic frequency threshold is adjusted to reflect the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    frequency_counter[obj.key] = 1
    last_access_timestamp[obj.key] = cache_snapshot.access_count
    cyclic_buffer.append(obj.key)
    # Adjust dynamic frequency threshold
    dynamic_frequency_threshold = max(1, sum(frequency_counter.values()) // len(frequency_counter))

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the cyclic buffer is updated to remove the evicted entry. The dynamic frequency threshold is recalibrated to account for the change in cache composition, ensuring it remains responsive to current access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    cyclic_buffer.remove(evicted_obj.key)
    del frequency_counter[evicted_obj.key]
    del last_access_timestamp[evicted_obj.key]
    # Recalibrate dynamic frequency threshold
    if frequency_counter:
        dynamic_frequency_threshold = max(1, sum(frequency_counter.values()) // len(frequency_counter))
    else:
        dynamic_frequency_threshold = INITIAL_DYNAMIC_THRESHOLD