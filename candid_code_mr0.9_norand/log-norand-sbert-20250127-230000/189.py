# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
import collections

# Put tunable constant parameters below
INITIAL_NEURAL_PLASTICITY_SCORE = 1
INITIAL_QUANTUM_ENTANGLEMENT_STATE = 1
INITIAL_HOLOGRAPHIC_PRIORITY_INDEX = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a quantum entanglement state matrix for cache lines, a neural plasticity score for adaptability, a topological vortex map for spatial locality, and a holographic principle-based priority index for data importance.
neural_plasticity_scores = {}
quantum_entanglement_states = {}
topological_vortex_map = collections.OrderedDict()
holographic_priority_indices = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the cache line with the lowest holographic priority index, factoring in the least entangled state and the lowest neural plasticity score, while considering the least significant position in the topological vortex map.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_priority = float('inf')
    
    for key in cache_snapshot.cache:
        priority = holographic_priority_indices[key]
        entanglement = quantum_entanglement_states[key]
        plasticity = neural_plasticity_scores[key]
        position = list(topological_vortex_map.keys()).index(key)
        
        if (priority, entanglement, plasticity, position) < (min_priority, float('inf'), float('inf'), float('inf')):
            min_priority = priority
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the neural plasticity score of the accessed cache line, updates its position in the topological vortex map to reflect recent access, and adjusts the quantum entanglement state to strengthen its connection with frequently accessed data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    neural_plasticity_scores[key] += 1
    quantum_entanglement_states[key] += 1
    
    # Move the accessed object to the end of the topological vortex map to reflect recent access
    topological_vortex_map.move_to_end(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its neural plasticity score, assigns it a position in the topological vortex map based on spatial locality, sets an initial quantum entanglement state, and calculates its holographic priority index based on initial data importance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    neural_plasticity_scores[key] = INITIAL_NEURAL_PLASTICITY_SCORE
    quantum_entanglement_states[key] = INITIAL_QUANTUM_ENTANGLEMENT_STATE
    holographic_priority_indices[key] = INITIAL_HOLOGRAPHIC_PRIORITY_INDEX
    
    # Insert the new object at the end of the topological vortex map
    topological_vortex_map[key] = None

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the quantum entanglement state matrix to remove the evicted line's influence, adjusts the topological vortex map to close the gap left by the eviction, and redistributes neural plasticity scores to maintain adaptability balance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove the evicted object's metadata
    del neural_plasticity_scores[evicted_key]
    del quantum_entanglement_states[evicted_key]
    del holographic_priority_indices[evicted_key]
    del topological_vortex_map[evicted_key]
    
    # Recalibrate the quantum entanglement state matrix
    for key in quantum_entanglement_states:
        quantum_entanglement_states[key] = max(1, quantum_entanglement_states[key] - 1)
    
    # Redistribute neural plasticity scores
    total_plasticity = sum(neural_plasticity_scores.values())
    for key in neural_plasticity_scores:
        neural_plasticity_scores[key] = max(1, neural_plasticity_scores[key] * len(neural_plasticity_scores) // total_plasticity)