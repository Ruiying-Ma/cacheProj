# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_QUANTUM_VARIABILITY = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a Quantum Variability score for each cache entry, a Temporal Equilibrium timestamp, an Adaptive Matrix that tracks access patterns, and a Neural Cohesion index that represents the relationship between cache entries.
quantum_variability = defaultdict(lambda: BASELINE_QUANTUM_VARIABILITY)
temporal_equilibrium = {}
adaptive_matrix = defaultdict(lambda: defaultdict(int))
neural_cohesion = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest Neural Cohesion index, adjusted by the Quantum Variability score, ensuring that entries with less cohesive relationships and lower variability are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = neural_cohesion[key] - quantum_variability[key]
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Quantum Variability score of the accessed entry is incremented, the Temporal Equilibrium timestamp is updated to the current time, and the Adaptive Matrix is adjusted to strengthen the relationship between the accessed entry and its neighbors, increasing their Neural Cohesion index.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    quantum_variability[key] += 1
    temporal_equilibrium[key] = cache_snapshot.access_count
    
    for neighbor_key in cache_snapshot.cache:
        if neighbor_key != key:
            adaptive_matrix[key][neighbor_key] += 1
            neural_cohesion[neighbor_key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its Quantum Variability score to a baseline value, sets the Temporal Equilibrium timestamp to the current time, and updates the Adaptive Matrix to establish initial relationships with existing entries, calculating an initial Neural Cohesion index.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    quantum_variability[key] = BASELINE_QUANTUM_VARIABILITY
    temporal_equilibrium[key] = cache_snapshot.access_count
    
    for existing_key in cache_snapshot.cache:
        if existing_key != key:
            adaptive_matrix[key][existing_key] = 1
            adaptive_matrix[existing_key][key] = 1
            neural_cohesion[key] += 1
            neural_cohesion[existing_key] += 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the Quantum Variability scores of remaining entries, updates the Temporal Equilibrium timestamps to reflect the new cache state, and adjusts the Adaptive Matrix to remove the influence of the evicted entry, recalculating Neural Cohesion indices accordingly.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove the evicted entry from the Adaptive Matrix and adjust Neural Cohesion
    for key in cache_snapshot.cache:
        if evicted_key in adaptive_matrix[key]:
            neural_cohesion[key] -= adaptive_matrix[key][evicted_key]
            del adaptive_matrix[key][evicted_key]
    
    # Remove the evicted entry's metadata
    if evicted_key in quantum_variability:
        del quantum_variability[evicted_key]
    if evicted_key in temporal_equilibrium:
        del temporal_equilibrium[evicted_key]
    if evicted_key in neural_cohesion:
        del neural_cohesion[evicted_key]