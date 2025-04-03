# Import anything you need below
from collections import deque, defaultdict

# Put tunable constant parameters below
ENTROPIC_TENSOR_WEIGHT = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a FIFO queue for basic ordering, a Quantum Field Dynamics matrix for interaction strengths, and an Entropic Tensor for access unpredictability.
fifo_queue = deque()
qfd_matrix = defaultdict(lambda: defaultdict(int))
entropic_tensor = defaultdict(float)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects a subset of cache entries from the front of the FIFO queue and evicts the one with the lowest interaction strength adjusted by the highest Entropic Tensor value.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    subset_size = min(len(fifo_queue), 5)  # Arbitrary subset size for eviction consideration
    candidates = list(fifo_queue)[:subset_size]
    
    min_score = float('inf')
    for key in candidates:
        interaction_strength = qfd_matrix[key][key]
        score = interaction_strength - ENTROPIC_TENSOR_WEIGHT * entropic_tensor[key]
        if score < min_score:
            min_score = score
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
    qfd_matrix[key][key] += 1
    entropic_tensor[key] = 1.0 / (1 + qfd_matrix[key][key])
    
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
    fifo_queue.append(key)
    qfd_matrix[key][key] = 1
    entropic_tensor[key] = 1.0

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
    if evicted_key in fifo_queue:
        fifo_queue.remove(evicted_key)
    if evicted_key in qfd_matrix:
        del qfd_matrix[evicted_key]
    if evicted_key in entropic_tensor:
        del entropic_tensor[evicted_key]