# Import anything you need below
import collections
import math

# Put tunable constant parameters below

# Put the metadata specifically maintained by the policy below. The policy maintains a combined LRU-FIFO queue, access frequency for each object, a pointer for cyclic traversal, and an Entropic Tensor for access unpredictability.
lru_fifo_queue = collections.OrderedDict()
access_frequency = collections.defaultdict(int)
pointer = 0
entropic_tensor = collections.defaultdict(float)

def calculate_entropic_tensor(cache_snapshot):
    total_accesses = cache_snapshot.access_count
    if total_accesses == 0:
        return
    for key, obj in cache_snapshot.cache.items():
        frequency = access_frequency[key]
        probability = frequency / total_accesses
        if probability > 0:
            entropic_tensor[key] = -probability * math.log(probability)
        else:
            entropic_tensor[key] = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The pointer starts from its current position and moves cyclically, setting the frequency of each object it encounters to 0 until it finds an object with zero frequency. From these zero-frequency objects, the one with the highest Entropic Tensor value is evicted. The evicted object is removed from the combined LRU-FIFO queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    global pointer
    candid_obj_key = None
    keys = list(lru_fifo_queue.keys())
    n = len(keys)
    
    while True:
        key = keys[pointer]
        access_frequency[key] = 0
        pointer = (pointer + 1) % n
        if access_frequency[key] == 0:
            break
    
    zero_freq_keys = [key for key in keys if access_frequency[key] == 0]
    candid_obj_key = max(zero_freq_keys, key=lambda k: entropic_tensor[k])
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    The frequency of the accessed object is set to 1. The Entropic Tensor is recalculated to reflect reduced disorder. The accessed object is moved to the most-recently-used end of the combined LRU-FIFO queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] = 1
    lru_fifo_queue.move_to_end(key)
    calculate_entropic_tensor(cache_snapshot)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    The inserted object's frequency is set to 1 and it is placed at the rear of the combined LRU-FIFO queue. The Entropic Tensor is recalculated to account for the new entry's unpredictability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] = 1
    lru_fifo_queue[key] = obj
    calculate_entropic_tensor(cache_snapshot)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    The evicted object is removed from the combined LRU-FIFO queue, and the remaining objects are moved one step forward. The Entropic Tensor is recalculated to reflect decreased disorder.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    del lru_fifo_queue[key]
    del access_frequency[key]
    del entropic_tensor[key]
    calculate_entropic_tensor(cache_snapshot)