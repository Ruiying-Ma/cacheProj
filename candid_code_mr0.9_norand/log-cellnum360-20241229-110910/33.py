# Import anything you need below
from collections import deque, defaultdict

# Put tunable constant parameters below
QUANTUM_FIELD_INITIAL_STRENGTH = 1
ENTROPIC_TENSOR_INITIAL_VALUE = 1

# Put the metadata specifically maintained by the policy below. The policy maintains two LRU queues (T1 and T2) and two FIFO ghost queues (B1 and B2) for recency tracking, along with a Quantum Field Dynamics matrix for interaction strengths and an Entropic Tensor for access unpredictability.
T1 = deque()
T2 = deque()
B1 = deque()
B2 = deque()
quantum_field_dynamics = defaultdict(lambda: defaultdict(int))
entropic_tensor = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects a subset of entries from T1 and T2, calculates a combined score using interaction strength and unpredictability, and evicts the entry with the lowest score. If T1 is not empty, preference is given to evicting from T1.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    def calculate_score(obj_key):
        interaction_strength = quantum_field_dynamics[obj_key][obj_key]
        unpredictability = entropic_tensor[obj_key]
        return interaction_strength + unpredictability

    if T1:
        # Prefer to evict from T1
        candid_obj_key = min(T1, key=calculate_score)
    else:
        # Evict from T2 if T1 is empty
        candid_obj_key = min(T2, key=calculate_score)

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the accessed entry is moved to the most-recently-used end of T2, its interaction strength in the Quantum Field Dynamics matrix is increased, and the Entropic Tensor is recalculated to reflect reduced disorder.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    obj_key = obj.key
    if obj_key in T1:
        T1.remove(obj_key)
    elif obj_key in T2:
        T2.remove(obj_key)
    T2.append(obj_key)
    quantum_field_dynamics[obj_key][obj_key] += 1
    entropic_tensor[obj_key] = max(0, entropic_tensor[obj_key] - 1)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is placed in T1 or T2 based on its previous presence in B1 or B2, the Quantum Field Dynamics matrix is updated with minimal initial interactions for the new entry, and the Entropic Tensor is recalculated to account for the new entry's unpredictability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    obj_key = obj.key
    if obj_key in B1:
        B1.remove(obj_key)
        T2.append(obj_key)
    elif obj_key in B2:
        B2.remove(obj_key)
        T2.append(obj_key)
    else:
        T1.append(obj_key)
    quantum_field_dynamics[obj_key][obj_key] = QUANTUM_FIELD_INITIAL_STRENGTH
    entropic_tensor[obj_key] = ENTROPIC_TENSOR_INITIAL_VALUE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the evicted entry is moved to the rear of its corresponding ghost queue (B1 or B2), the Quantum Field Dynamics matrix is updated by removing the evicted entry's interactions, and the Entropic Tensor is recalculated to reflect decreased disorder.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in T1:
        T1.remove(evicted_key)
        B1.append(evicted_key)
    elif evicted_key in T2:
        T2.remove(evicted_key)
        B2.append(evicted_key)
    if evicted_key in quantum_field_dynamics:
        del quantum_field_dynamics[evicted_key]
    if evicted_key in entropic_tensor:
        del entropic_tensor[evicted_key]