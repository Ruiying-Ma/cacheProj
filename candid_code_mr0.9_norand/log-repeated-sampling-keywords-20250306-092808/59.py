# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import heapq

# Put tunable constant parameters below

# Put the metadata specifically maintained by the policy below. The policy maintains a min-heap structure where each node contains a frequency counter and a timestamp for each cached object.
heap = []
metadata = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the object with the lowest frequency counter. If there is a tie, it evicts the object with the oldest timestamp.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    if heap:
        candid_obj_key = heapq.heappop(heap)[2]
        del metadata[candid_obj_key]
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the frequency counter of the accessed object is incremented by one, and its timestamp is updated to the current time. The heap is then restructured to maintain the min-heap property.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    if key in metadata:
        freq, _, _ = metadata[key]
        new_entry = (freq + 1, cache_snapshot.access_count, key)
        metadata[key] = new_entry
        heapq.heappush(heap, new_entry)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its frequency counter is initialized to one, and its timestamp is set to the current time. The object is then added to the heap, and the heap is restructured to maintain the min-heap property.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    new_entry = (1, cache_snapshot.access_count, key)
    metadata[key] = new_entry
    heapq.heappush(heap, new_entry)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting the victim, the object is removed from the heap. No further updates to the metadata are necessary as the heap automatically restructures itself to maintain the min-heap property.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    key = evicted_obj.key
    if key in metadata:
        del metadata[key]