# Import anything you need below
from collections import deque, defaultdict

# Put tunable constant parameters below
DECAY_FACTOR = 0.9  # Decay factor to reduce the importance of older accesses

# Put the metadata specifically maintained by the policy below. The policy maintains a circular buffer to track cache entries, an access latency counter for each entry, and a decay factor that reduces the importance of older accesses over time.
circular_buffer = deque()  # Circular buffer to track cache entries
access_latency = defaultdict(float)  # Access latency counter for each entry

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the highest decayed latency value, indicating it has been accessed less frequently or less recently compared to others.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    max_latency = -1
    for key in circular_buffer:
        if access_latency[key] > max_latency:
            max_latency = access_latency[key]
            candid_obj_key = key
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access latency counter for the accessed entry is incremented, and the decay algorithm is applied to all entries to reduce their latency values over time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    # Increment the access latency counter for the accessed entry
    access_latency[obj.key] += 1

    # Apply the decay algorithm to all entries
    for key in access_latency:
        access_latency[key] *= DECAY_FACTOR

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the entry is added to the circular buffer, its access latency counter is initialized, and the decay algorithm is applied to all existing entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    # Add the entry to the circular buffer
    circular_buffer.append(obj.key)

    # Initialize its access latency counter
    access_latency[obj.key] = 0

    # Apply the decay algorithm to all existing entries
    for key in access_latency:
        access_latency[key] *= DECAY_FACTOR

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the circular buffer is updated to remove the evicted entry, and the decay algorithm is applied to the remaining entries to ensure their latency values reflect their current relevance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    # Remove the evicted entry from the circular buffer
    circular_buffer.remove(evicted_obj.key)

    # Remove the evicted entry's latency counter
    del access_latency[evicted_obj.key]

    # Apply the decay algorithm to the remaining entries
    for key in access_latency:
        access_latency[key] *= DECAY_FACTOR