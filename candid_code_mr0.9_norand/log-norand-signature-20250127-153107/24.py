# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
from collections import deque, defaultdict

# Put tunable constant parameters below
SQ_CAPACITY = 100  # Example capacity for SQ
MQ_CAPACITY = 100  # Example capacity for MQ
GQ_CAPACITY = 100  # Example capacity for GQ

# Put the metadata specifically maintained by the policy below. The system maintains two FIFO queues (SQ and MQ) within the cache, a ghost FIFO queue (GQ) outside the cache, and a single pointer that traverses the cache in a circular manner. It also tracks the access frequency of each cached object.
SQ = deque()
MQ = deque()
GQ = deque()
pointer = 0
frequency = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    If SQ exceeds its capacity, objects are moved from SQ to MQ until an object with frequency less than 2 is found or MQ is full. If MQ is full, the pointer traverses MQ, setting frequencies to 0 until it finds an object with zero frequency to evict. If SQ is not full, the object with frequency less than 2 is evicted. Evicted objects are added to GQ.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    global pointer
    candid_obj_key = None

    if len(SQ) >= SQ_CAPACITY:
        while SQ and (frequency[SQ[0].key] >= 2 or len(MQ) >= MQ_CAPACITY):
            if len(MQ) < MQ_CAPACITY:
                MQ.append(SQ.popleft())
            else:
                while True:
                    if pointer >= len(MQ):
                        pointer = 0
                    if frequency[MQ[pointer].key] == 0:
                        candid_obj_key = MQ[pointer].key
                        MQ.remove(MQ[pointer])
                        break
                    frequency[MQ[pointer].key] = 0
                    pointer += 1
                break
        if not candid_obj_key:
            candid_obj_key = SQ.popleft().key
    else:
        for obj in SQ:
            if frequency[obj.key] < 2:
                candid_obj_key = obj.key
                SQ.remove(obj)
                break

    if candid_obj_key:
        GQ.append(candid_obj_key)
        if len(GQ) > GQ_CAPACITY:
            GQ.popleft()

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    If the hit object is in SQ or MQ and its frequency is less than 3, increase its frequency by 1. The pointer does not move.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    if obj.key in [o.key for o in SQ] or obj.key in [o.key for o in MQ]:
        if frequency[obj.key] < 3:
            frequency[obj.key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    Set the inserted object's frequency to 1. If it was in GQ, place it at the rear of MQ and remove it from GQ. Otherwise, place it at the rear of SQ. The pointer does not move.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    frequency[obj.key] = 1
    if obj.key in GQ:
        GQ.remove(obj.key)
        MQ.append(obj)
    else:
        SQ.append(obj)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Add the evicted object to the rear of GQ. If GQ is full, remove its front object. The pointer does not move.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    GQ.append(evicted_obj.key)
    if len(GQ) > GQ_CAPACITY:
        GQ.popleft()