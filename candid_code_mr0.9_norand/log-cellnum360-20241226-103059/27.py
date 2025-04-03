# Import anything you need below
from collections import deque
import numpy as np

# Put tunable constant parameters below
ENTROPIC_TENSOR_INITIAL_VALUE = 1.0
INTERACTION_STRENGTH_INITIAL_VALUE = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a FIFO queue, a Quantum Field Dynamics matrix for interaction strengths, and an Entropic Tensor for access unpredictability. The FIFO queue tracks the order of entries, while the matrix and tensor provide dynamic interaction and unpredictability metrics.
fifo_queue = deque()
interaction_matrix = {}
entropic_tensor = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects a subset of cache entries, prioritizing those at the front of the FIFO queue, and evicts the entry with the lowest interaction strength adjusted by the highest Entropic Tensor value.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_metric = float('inf')
    for key in list(fifo_queue)[:min(len(fifo_queue), 10)]:  # Consider a subset of the FIFO queue
        interaction_strength = interaction_matrix.get(key, INTERACTION_STRENGTH_INITIAL_VALUE)
        entropy_value = entropic_tensor.get(key, ENTROPIC_TENSOR_INITIAL_VALUE)
        metric = interaction_strength / entropy_value
        if metric < min_metric:
            min_metric = metric
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the interaction strength of the accessed entry in the Quantum Field Dynamics matrix is increased, the Entropic Tensor is recalculated to reflect reduced disorder, and the entry is moved to the rear of the FIFO queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    # Increase interaction strength
    interaction_matrix[key] = interaction_matrix.get(key, INTERACTION_STRENGTH_INITIAL_VALUE) + 1
    # Recalculate Entropic Tensor
    entropic_tensor[key] = max(ENTROPIC_TENSOR_INITIAL_VALUE, entropic_tensor.get(key, ENTROPIC_TENSOR_INITIAL_VALUE) - 0.1)
    # Move to rear of FIFO queue
    if key in fifo_queue:
        fifo_queue.remove(key)
    fifo_queue.append(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is placed at the rear of the FIFO queue, the Quantum Field Dynamics matrix is expanded to include the new entry with minimal initial interactions, and the Entropic Tensor is recalculated to account for the new entry's unpredictability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    # Place at rear of FIFO queue
    fifo_queue.append(key)
    # Expand Quantum Field Dynamics matrix
    interaction_matrix[key] = INTERACTION_STRENGTH_INITIAL_VALUE
    # Recalculate Entropic Tensor
    entropic_tensor[key] = ENTROPIC_TENSOR_INITIAL_VALUE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the evicted entry is removed from the front of the FIFO queue, the Quantum Field Dynamics matrix is updated by removing the evicted entry's interactions, and the Entropic Tensor is recalculated to reflect decreased disorder.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    # Remove from FIFO queue
    if evicted_key in fifo_queue:
        fifo_queue.remove(evicted_key)
    # Update Quantum Field Dynamics matrix
    if evicted_key in interaction_matrix:
        del interaction_matrix[evicted_key]
    # Recalculate Entropic Tensor
    if evicted_key in entropic_tensor:
        del entropic_tensor[evicted_key]