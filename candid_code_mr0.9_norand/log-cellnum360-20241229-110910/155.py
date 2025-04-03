# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASE_TEMPORAL_STABILITY_SCORE = 10
QUANTUM_STATE_NEUTRAL = 0
QUANTUM_STATE_ADJUSTMENT = 1
TEMPORAL_STABILITY_INCREMENT = 5
HEURISTIC_DECAY_FACTOR = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains a frequency counter for each cache entry, a heuristic map that associates access patterns with specific cache entries, a temporal stability score indicating the likelihood of future accesses, and a quantum state that represents the entry's readiness for transition (eviction).
frequency_counter = defaultdict(int)
heuristic_map = defaultdict(float)
temporal_stability_score = defaultdict(lambda: BASE_TEMPORAL_STABILITY_SCORE)
quantum_state = defaultdict(lambda: QUANTUM_STATE_NEUTRAL)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest temporal stability score, adjusted by its quantum state. If multiple entries have similar scores, the heuristic map is consulted to determine which entry is least likely to be accessed soon.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = temporal_stability_score[key] + quantum_state[key]
        if score < min_score:
            min_score = score
            candid_obj_key = key
        elif score == min_score:
            if heuristic_map[key] < heuristic_map[candid_obj_key]:
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the frequency counter for the accessed entry is incremented, the heuristic map is updated to reinforce the current access pattern, the temporal stability score is increased to reflect the recent access, and the quantum state is adjusted to reflect a lower readiness for transition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    frequency_counter[obj.key] += 1
    heuristic_map[obj.key] += 1
    temporal_stability_score[obj.key] += TEMPORAL_STABILITY_INCREMENT
    quantum_state[obj.key] -= QUANTUM_STATE_ADJUSTMENT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the frequency counter is initialized to one, the heuristic map is updated to include the new access pattern, the temporal stability score is set to a baseline value, and the quantum state is initialized to a neutral position indicating neither high nor low readiness for transition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    frequency_counter[obj.key] = 1
    heuristic_map[obj.key] = 1
    temporal_stability_score[obj.key] = BASE_TEMPORAL_STABILITY_SCORE
    quantum_state[obj.key] = QUANTUM_STATE_NEUTRAL

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the heuristic map is adjusted to reduce the weight of the evicted entry's access pattern, the temporal stability scores of remaining entries are recalibrated to reflect the new cache state, and the quantum states of all entries are slightly adjusted to account for the change in cache dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    heuristic_map[evicted_obj.key] *= HEURISTIC_DECAY_FACTOR
    del frequency_counter[evicted_obj.key]
    del temporal_stability_score[evicted_obj.key]
    del quantum_state[evicted_obj.key]
    
    for key in cache_snapshot.cache:
        temporal_stability_score[key] = max(BASE_TEMPORAL_STABILITY_SCORE, temporal_stability_score[key] - 1)
        quantum_state[key] += QUANTUM_STATE_ADJUSTMENT