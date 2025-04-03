# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import heapq

# Put tunable constant parameters below

# Put the metadata specifically maintained by the policy below. The policy maintains a dictionary that tracks the access time and frequency of each cache entry, as well as a secondary priority queue to prioritize entries based on the quotient of access time and frequency.
metadata = {
    'access_time': {},  # Dictionary to track access time of each object
    'access_frequency': {},  # Dictionary to track access frequency of each object
    'priority_queue': []  # Priority queue to prioritize entries based on the quotient of access time and frequency
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim based on the lowest quotient of access time by access frequency, targeting entries that are accessed often but have lower access recency, promoting a balance between recency and frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    while metadata['priority_queue']:
        quotient, key = heapq.heappop(metadata['priority_queue'])
        if key in cache_snapshot.cache:
            candid_obj_key = key
            break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access time for the entry is updated to the current time, the access frequency is incremented by one, and the entry's position in the priority queue is recalculated based on the updated quotient.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    current_time = cache_snapshot.access_count
    metadata['access_time'][key] = current_time
    metadata['access_frequency'][key] += 1
    quotient = current_time / metadata['access_frequency'][key]
    heapq.heappush(metadata['priority_queue'], (quotient, key))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object into the cache, the access time is set to the current time, the access frequency is initialized to one, and the object is added to the priority queue with its initial quotient value.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    current_time = cache_snapshot.access_count
    metadata['access_time'][key] = current_time
    metadata['access_frequency'][key] = 1
    quotient = current_time / metadata['access_frequency'][key]
    heapq.heappush(metadata['priority_queue'], (quotient, key))

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Immediately after eviction, the corresponding entry is removed from both the dictionary and the priority queue, ensuring that the metadata reflects the current state of the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    key = evicted_obj.key
    if key in metadata['access_time']:
        del metadata['access_time'][key]
    if key in metadata['access_frequency']:
        del metadata['access_frequency'][key]
    # No need to remove from priority queue explicitly as it will be ignored in future evictions