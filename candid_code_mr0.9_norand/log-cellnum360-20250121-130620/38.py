# Import anything you need below
import numpy as np

# Put tunable constant parameters below
INITIAL_INTERACTION_STRENGTH = 0.1
ENTROPIC_TENSOR_INITIAL_VALUE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a FIFO queue, access frequency for each cached object, a pointer for cyclic traversal, a Quantum Field Dynamics matrix for interaction strengths, and an Entropic Tensor for access unpredictability.
fifo_queue = []
access_frequency = {}
pointer = 0
qfd_matrix = {}
entropic_tensor = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy starts from the current pointer position and moves cyclically, setting frequencies to 0 until it finds an object with zero frequency. It then selects a subset of these zero-frequency objects and evicts the one with the lowest interaction strength adjusted by the highest Entropic Tensor value.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    global pointer
    zero_freq_objects = []
    n = len(fifo_queue)
    
    for _ in range(n):
        current_key = fifo_queue[pointer]
        if access_frequency[current_key] == 0:
            zero_freq_objects.append(current_key)
        else:
            access_frequency[current_key] = 0
        pointer = (pointer + 1) % n
    
    if not zero_freq_objects:
        zero_freq_objects.append(fifo_queue[pointer])
    
    min_value = float('inf')
    candid_obj_key = zero_freq_objects[0]
    
    for key in zero_freq_objects:
        interaction_strength = qfd_matrix[key]
        entropic_value = entropic_tensor[key]
        value = interaction_strength - entropic_value
        if value < min_value:
            min_value = value
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the frequency of the accessed object is set to 1 without moving it. The interaction strength in the Quantum Field Dynamics matrix is slightly increased, and the Entropic Tensor is recalculated to reflect reduced disorder.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] = 1
    qfd_matrix[key] += 0.01
    entropic_tensor[key] = 1 / (1 + np.log(1 + qfd_matrix[key]))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its frequency is set to 1 and it is placed at the rear of the FIFO queue. The Quantum Field Dynamics matrix is expanded to include the new entry with minimal initial interactions, and the Entropic Tensor is recalculated to account for the new entry's unpredictability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    fifo_queue.append(key)
    access_frequency[key] = 1
    qfd_matrix[key] = INITIAL_INTERACTION_STRENGTH
    entropic_tensor[key] = ENTROPIC_TENSOR_INITIAL_VALUE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the evicted object is removed from the FIFO queue, and the remaining objects are moved one step forward. The Quantum Field Dynamics matrix is updated by removing the evicted entry's interactions, and the Entropic Tensor is recalculated to reflect decreased disorder.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    fifo_queue.remove(key)
    del access_frequency[key]
    del qfd_matrix[key]
    del entropic_tensor[key]