# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_UTILITY_SCORE = 1.0
INITIAL_PHASE = 0
NEUTRAL_TEMPORAL_FLUX = 0.0
UTILITY_INCREMENT = 0.5
TEMPORAL_FLUX_INCREMENT = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains a Neural Dynamics Map that tracks the access patterns of cache entries, an Adaptive Phase Linkage that identifies the phase of usage for each entry, a Cognitive Continuum that ranks entries based on their predicted future utility, and a Temporal Flux Modulation that adjusts the priority of entries based on recent temporal access trends.
neural_dynamics_map = defaultdict(lambda: 0)
adaptive_phase_linkage = defaultdict(lambda: INITIAL_PHASE)
cognitive_continuum = defaultdict(lambda: INITIAL_UTILITY_SCORE)
temporal_flux_modulation = defaultdict(lambda: NEUTRAL_TEMPORAL_FLUX)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the entry with the lowest combined score from the Cognitive Continuum and Temporal Flux Modulation, ensuring that entries with low predicted future utility and low recent access frequency are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        score = cognitive_continuum[key] + temporal_flux_modulation[key]
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Neural Dynamics Map is updated to reinforce the access pattern of the hit entry, the Adaptive Phase Linkage is adjusted to reflect the current phase of usage, the Cognitive Continuum score is increased to reflect higher predicted utility, and the Temporal Flux Modulation is recalibrated to increase the entry's priority based on recent access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    neural_dynamics_map[key] += 1
    adaptive_phase_linkage[key] += 1
    cognitive_continuum[key] += UTILITY_INCREMENT
    temporal_flux_modulation[key] += TEMPORAL_FLUX_INCREMENT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Neural Dynamics Map is initialized with a baseline access pattern, the Adaptive Phase Linkage is set to an initial phase, the Cognitive Continuum assigns a preliminary utility score based on initial predictions, and the Temporal Flux Modulation is set to a neutral state awaiting further access data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    neural_dynamics_map[key] = 1
    adaptive_phase_linkage[key] = INITIAL_PHASE
    cognitive_continuum[key] = INITIAL_UTILITY_SCORE
    temporal_flux_modulation[key] = NEUTRAL_TEMPORAL_FLUX

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the Neural Dynamics Map is adjusted to remove the evicted entry's pattern, the Adaptive Phase Linkage is recalibrated to reflect the removal, the Cognitive Continuum is updated to redistribute utility scores among remaining entries, and the Temporal Flux Modulation is recalibrated to adjust the priority of remaining entries based on the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    del neural_dynamics_map[evicted_key]
    del adaptive_phase_linkage[evicted_key]
    del cognitive_continuum[evicted_key]
    del temporal_flux_modulation[evicted_key]
    
    # Optionally, adjust remaining entries if needed
    for key in cache_snapshot.cache:
        cognitive_continuum[key] *= 0.95  # Example adjustment
        temporal_flux_modulation[key] *= 0.95  # Example adjustment