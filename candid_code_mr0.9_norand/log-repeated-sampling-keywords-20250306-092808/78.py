# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque
import heapq

# Put tunable constant parameters below
INITIAL_PRIORITY = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a circular buffer to track the order of cache entries, a priority queue to manage the priority of each entry based on access frequency and recency, and a load balance counter to ensure even distribution of cache usage.
circular_buffer = deque()
priority_queue = []
priority_dict = {}
load_balance_counter = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest priority from the priority queue. If there is a tie, it uses the circular buffer to select the oldest entry among the tied candidates.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    while priority_queue:
        lowest_priority, key = heapq.heappop(priority_queue)
        if key in cache_snapshot.cache:
            candid_obj_key = key
            break

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the priority of the accessed entry in the priority queue and updates its position in the circular buffer to reflect its recent use.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    if key in priority_dict:
        priority_dict[key] += 1
        heapq.heappush(priority_queue, (priority_dict[key], key))
    if key in circular_buffer:
        circular_buffer.remove(key)
    circular_buffer.append(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy adds the new entry to the circular buffer and assigns it an initial priority in the priority queue. The load balance counter is incremented to reflect the new addition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    priority_dict[key] = INITIAL_PRIORITY
    heapq.heappush(priority_queue, (INITIAL_PRIORITY, key))
    circular_buffer.append(key)
    global load_balance_counter
    load_balance_counter += 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes the evicted entry from both the circular buffer and the priority queue. The load balance counter is decremented to reflect the removal.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    key = evicted_obj.key
    if key in priority_dict:
        del priority_dict[key]
    if key in circular_buffer:
        circular_buffer.remove(key)
    global load_balance_counter
    load_balance_counter -= 1