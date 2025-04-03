# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import defaultdict
import heapq

# Put tunable constant parameters below

# Put the metadata specifically maintained by the policy below. The policy maintains a frequency count, a timestamp of the last access, and a position in a priority queue for each cached object.
frequency_count = defaultdict(int)
last_access_time = {}
priority_queue = []

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the object with the lowest frequency count. If there is a tie, it selects the object with the oldest timestamp. The priority queue helps efficiently manage and retrieve the eviction candidate.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    while priority_queue:
        freq, timestamp, key = heapq.heappop(priority_queue)
        if key in cache_snapshot.cache:
            candid_obj_key = key
            break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the frequency count, updates the timestamp to the current time, and repositions the object in the priority queue based on the updated frequency and timestamp.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    frequency_count[key] += 1
    last_access_time[key] = cache_snapshot.access_count
    heapq.heappush(priority_queue, (frequency_count[key], last_access_time[key], key))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the frequency count to 1, sets the timestamp to the current time, and places the object in the appropriate position in the priority queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    frequency_count[key] = 1
    last_access_time[key] = cache_snapshot.access_count
    heapq.heappush(priority_queue, (frequency_count[key], last_access_time[key], key))

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy removes the object's metadata from the frequency tracker, timestamp manager, and priority queue, ensuring the cache metadata remains consistent and up-to-date.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    key = evicted_obj.key
    if key in frequency_count:
        del frequency_count[key]
    if key in last_access_time:
        del last_access_time[key]
    # Rebuild the priority queue to remove the evicted object
    global priority_queue
    priority_queue = [(freq, ts, k) for freq, ts, k in priority_queue if k != key]
    heapq.heapify(priority_queue)