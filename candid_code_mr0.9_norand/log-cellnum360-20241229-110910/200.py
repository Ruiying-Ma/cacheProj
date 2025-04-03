# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
DEFAULT_ENTROPIC_STABILITY = 1.0
NEUTRAL_QUANTUM_FLUX = 0.5
STABILITY_INCREMENT = 0.1
FLUX_DECREMENT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a Temporal Matrix to track access patterns over time, a Quantum Flux indicator to measure the dynamic state of cache entries, and an Entropic Stability score to assess the predictability of future accesses.
temporal_matrix = defaultdict(lambda: [])
quantum_flux = defaultdict(lambda: NEUTRAL_QUANTUM_FLUX)
entropic_stability = defaultdict(lambda: DEFAULT_ENTROPIC_STABILITY)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the entry with the lowest Entropic Stability score, indicating unpredictable future access, and the highest Quantum Flux, suggesting it is in a volatile state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_stability = float('inf')
    max_flux = float('-inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        stability = entropic_stability[key]
        flux = quantum_flux[key]
        
        if stability < min_stability or (stability == min_stability and flux > max_flux):
            min_stability = stability
            max_flux = flux
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Temporal Matrix is updated to reflect the recent access, the Quantum Flux is recalibrated to a lower state due to increased stability, and the Entropic Stability score is incremented to reflect improved predictability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    temporal_matrix[key].append(cache_snapshot.access_count)
    quantum_flux[key] = max(0, quantum_flux[key] - FLUX_DECREMENT)
    entropic_stability[key] += STABILITY_INCREMENT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Temporal Matrix is initialized with a baseline access pattern, the Quantum Flux is set to a neutral state, and the Entropic Stability score is set to a default value indicating unknown predictability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    temporal_matrix[key] = [cache_snapshot.access_count]
    quantum_flux[key] = NEUTRAL_QUANTUM_FLUX
    entropic_stability[key] = DEFAULT_ENTROPIC_STABILITY

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the Temporal Matrix is adjusted to remove the evicted entry's data, the Quantum Flux of remaining entries is recalculated to reflect the new cache state, and the Entropic Stability scores are normalized to maintain balance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in temporal_matrix:
        del temporal_matrix[evicted_key]
    if evicted_key in quantum_flux:
        del quantum_flux[evicted_key]
    if evicted_key in entropic_stability:
        del entropic_stability[evicted_key]
    
    # Normalize entropic stability scores
    total_stability = sum(entropic_stability.values())
    if total_stability > 0:
        for key in entropic_stability:
            entropic_stability[key] /= total_stability