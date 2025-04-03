# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
import collections

# Put tunable constant parameters below
SYNC_PRIORITY_WEIGHT = 1
ACCESS_FREQUENCY_WEIGHT = 1
LAST_ACCESS_TIME_WEIGHT = 1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, and data synchronization status for each cache entry. It also keeps a global counter for total cache accesses and a synchronization queue for pending data sync operations.
access_frequency = collections.defaultdict(int)
last_access_timestamp = collections.defaultdict(int)
sync_status = collections.defaultdict(bool)
sync_queue = collections.deque()
global_access_counter = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a weighted score combining low access frequency, old access timestamp, and low synchronization priority. Entries with the lowest scores are evicted first to balance cache hit ratio and data synchronization needs.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (ACCESS_FREQUENCY_WEIGHT * access_frequency[key] +
                 LAST_ACCESS_TIME_WEIGHT * (global_access_counter - last_access_timestamp[key]) +
                 SYNC_PRIORITY_WEIGHT * (1 if sync_status[key] else 0))
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency and last access timestamp of the hit entry are updated. The global counter for total cache accesses is incremented. If the entry requires synchronization, it is moved up in the synchronization queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    global global_access_counter
    global_access_counter += 1
    access_frequency[obj.key] += 1
    last_access_timestamp[obj.key] = global_access_counter
    
    if sync_status[obj.key]:
        sync_queue.remove(obj.key)
        sync_queue.appendleft(obj.key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its access frequency is initialized, and the current timestamp is recorded as the last access time. The global counter for total cache accesses is incremented. If the object requires synchronization, it is added to the synchronization queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    global global_access_counter
    global_access_counter += 1
    access_frequency[obj.key] = 1
    last_access_timestamp[obj.key] = global_access_counter
    sync_status[obj.key] = False  # Assuming new objects do not require sync initially
    
    if sync_status[obj.key]:
        sync_queue.append(obj.key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes its metadata, decrements the global counter for total cache accesses, and updates the synchronization queue to remove any pending operations related to the evicted entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    global global_access_counter
    global_access_counter -= 1
    del access_frequency[evicted_obj.key]
    del last_access_timestamp[evicted_obj.key]
    if evicted_obj.key in sync_status:
        del sync_status[evicted_obj.key]
    if evicted_obj.key in sync_queue:
        sync_queue.remove(evicted_obj.key)