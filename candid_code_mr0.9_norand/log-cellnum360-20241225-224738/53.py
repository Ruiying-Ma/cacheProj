# Import anything you need below
import threading

# Put tunable constant parameters below
LFU_WEIGHT = 0.5
LRU_WEIGHT = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, and a thread ownership flag for each cache entry. It also tracks a global sequential consistency counter to ensure operations are applied in order.
metadata = {}
global_sequential_counter = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a hybrid score that combines the least frequently used and least recently used metrics, adjusted by the thread ownership flag to prioritize eviction of entries not currently owned by active threads.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        if key not in metadata:
            continue
        
        access_freq = metadata[key]['access_frequency']
        last_access_time = metadata[key]['last_access_time']
        thread_owner = metadata[key]['thread_owner']
        
        # Calculate hybrid score
        lfu_score = access_freq
        lru_score = cache_snapshot.access_count - last_access_time
        hybrid_score = (LFU_WEIGHT * lfu_score) + (LRU_WEIGHT * lru_score)
        
        # Adjust score based on thread ownership
        if thread_owner != threading.current_thread():
            hybrid_score *= 0.5  # Prioritize eviction of non-owned entries
        
        if hybrid_score < min_score:
            min_score = hybrid_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency is incremented, the last access timestamp is updated to the current time, and the thread ownership flag is set to the current thread. The global sequential consistency counter is incremented to reflect the operation.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    global global_sequential_counter
    key = obj.key
    
    if key in metadata:
        metadata[key]['access_frequency'] += 1
        metadata[key]['last_access_time'] = cache_snapshot.access_count
        metadata[key]['thread_owner'] = threading.current_thread()
    
    global_sequential_counter += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the access frequency is initialized to one, the last access timestamp is set to the current time, and the thread ownership flag is set to the current thread. The global sequential consistency counter is incremented.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    global global_sequential_counter
    key = obj.key
    
    metadata[key] = {
        'access_frequency': 1,
        'last_access_time': cache_snapshot.access_count,
        'thread_owner': threading.current_thread()
    }
    
    global_sequential_counter += 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the metadata for the evicted entry is cleared. The global sequential consistency counter is incremented to maintain order, and any thread ownership flags are reset to ensure no stale ownership remains.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    global global_sequential_counter
    evicted_key = evicted_obj.key
    
    if evicted_key in metadata:
        del metadata[evicted_key]
    
    global_sequential_counter += 1