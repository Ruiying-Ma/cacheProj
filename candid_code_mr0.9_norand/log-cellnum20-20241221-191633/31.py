# Import anything you need below
import heapq
import threading

# Put tunable constant parameters below

# Put the metadata specifically maintained by the policy below. The policy maintains a priority queue of cache entries based on access frequency and recency, a semaphore for each cache entry to ensure mutual exclusion, and a global semaphore to prevent deadlock by controlling the number of concurrent cache operations.
priority_queue = []  # Min-heap based on (frequency, last_access_time, obj_key)
access_frequency = {}  # Dictionary to store access frequency of each object
last_access_time = {}  # Dictionary to store last access time of each object
entry_semaphores = {}  # Dictionary to store semaphores for each cache entry
global_semaphore = threading.Semaphore(1)  # Global semaphore for controlling concurrent operations

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache entry with the lowest priority in the priority queue, which is determined by a combination of least frequency and oldest access time, ensuring that the semaphore for this entry is available.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    while priority_queue:
        freq, last_time, key = heapq.heappop(priority_queue)
        if entry_semaphores[key].acquire(blocking=False):
            candid_obj_key = key
            break
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the access frequency of the entry, updates its last access time, and signals the semaphore associated with the entry to allow other operations to proceed.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    access_frequency[key] += 1
    last_access_time[key] = cache_snapshot.access_count
    heapq.heappush(priority_queue, (access_frequency[key], last_access_time[key], key))
    entry_semaphores[key].release()

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency to one, sets its last access time to the current time, and signals the semaphore for the new entry to ensure it is available for future operations.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    access_frequency[key] = 1
    last_access_time[key] = cache_snapshot.access_count
    heapq.heappush(priority_queue, (access_frequency[key], last_access_time[key], key))
    entry_semaphores[key] = threading.Semaphore(1)
    entry_semaphores[key].release()

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes the entry from the priority queue, releases its semaphore, and signals the global semaphore to allow other cache operations to proceed, maintaining system stability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    key = evicted_obj.key
    if key in access_frequency:
        del access_frequency[key]
    if key in last_access_time:
        del last_access_time[key]
    if key in entry_semaphores:
        entry_semaphores[key].release()
        del entry_semaphores[key]
    global_semaphore.release()