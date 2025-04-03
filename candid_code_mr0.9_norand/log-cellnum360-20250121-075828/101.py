# Import anything you need below
from collections import deque

# Put tunable constant parameters below

# Put the metadata specifically maintained by the policy below. The policy maintains a combined LRU-FIFO queue and a pointer for cyclic traversal. No other metadata such as access frequency, Quantum Field Dynamics matrix, or Entropic Tensor is maintained.
lru_fifo_queue = deque()
pointer = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    During eviction, the pointer starts from its current position and moves cyclically. The first object it encounters is evicted. This process does not involve any additional metadata.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    global pointer
    candid_obj_key = None
    # Your code below
    while True:
        if pointer >= len(lru_fifo_queue):
            pointer = 0
        candid_obj_key = lru_fifo_queue[pointer]
        pointer += 1
        if candid_obj_key in cache_snapshot.cache:
            break
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Immediately after a hit, the accessed object is moved to the most-recently-used end of the combined LRU-FIFO queue. No other metadata is updated.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    global lru_fifo_queue
    # Your code below
    if obj.key in lru_fifo_queue:
        lru_fifo_queue.remove(obj.key)
    lru_fifo_queue.append(obj.key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    Immediately after insertion, the inserted object is placed at the rear of the combined LRU-FIFO queue. No other metadata is updated.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    global lru_fifo_queue
    # Your code below
    lru_fifo_queue.append(obj.key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Immediately after eviction, the evicted object is removed from the combined LRU-FIFO queue. No other metadata is updated.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    global lru_fifo_queue
    # Your code below
    if evicted_obj.key in lru_fifo_queue:
        lru_fifo_queue.remove(evicted_obj.key)