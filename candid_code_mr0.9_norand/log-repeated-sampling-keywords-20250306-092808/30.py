# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque
import heapq

# Put tunable constant parameters below

# Put the metadata specifically maintained by the policy below. The policy maintains a circular buffer to track the order of cache entries, an access counter for each entry to track the number of accesses, and a priority queue to manage entries based on their access frequency and recency.
circular_buffer = deque()
access_counter = {}
priority_queue = []

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest priority in the priority queue, which is determined by a combination of its access frequency and recency. If there is a tie, the entry that appears earliest in the circular buffer is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    while priority_queue:
        _, _, candid_obj_key = heapq.heappop(priority_queue)
        if candid_obj_key in cache_snapshot.cache:
            break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access counter for the corresponding entry is incremented, and the entry's position in the priority queue is updated to reflect its increased priority. The circular buffer remains unchanged.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    access_counter[obj.key] += 1
    heapq.heappush(priority_queue, (access_counter[obj.key], cache_snapshot.access_count, obj.key))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the object is added to the circular buffer, its access counter is initialized to 1, and it is inserted into the priority queue with its initial priority based on the access counter and insertion time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    circular_buffer.append(obj.key)
    access_counter[obj.key] = 1
    heapq.heappush(priority_queue, (access_counter[obj.key], cache_snapshot.access_count, obj.key))

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the entry is removed from the circular buffer, its access counter is deleted, and it is removed from the priority queue. The circular buffer is then updated to reflect the removal.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    circular_buffer.remove(evicted_obj.key)
    del access_counter[evicted_obj.key]
    # No need to remove from priority_queue explicitly as it will be ignored in future evictions