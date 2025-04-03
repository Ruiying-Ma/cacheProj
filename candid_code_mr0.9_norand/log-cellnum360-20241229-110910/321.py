# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_ECHO_SCORE = 1
NEUTRAL_STABILIZATION_PULSE = 0

# Put the metadata specifically maintained by the policy below. The policy maintains a 'Computational Echo' score for each cache entry, a 'Divergence Map' that tracks access patterns, a 'Stabilization Pulse' that records the frequency of access changes, and an 'Equilibrium Shift' indicator that reflects the balance between recent and historical access patterns.
computational_echo = defaultdict(lambda: INITIAL_ECHO_SCORE)
divergence_map = defaultdict(int)
stabilization_pulse = defaultdict(lambda: NEUTRAL_STABILIZATION_PULSE)
equilibrium_shift = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the entry with the lowest 'Computational Echo' score, adjusted by the 'Equilibrium Shift' to favor entries with stable access patterns over time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        adjusted_score = computational_echo[key] - equilibrium_shift
        if adjusted_score < min_score:
            min_score = adjusted_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the 'Computational Echo' score of the accessed entry is incremented, the 'Divergence Map' is updated to reflect the new access pattern, and the 'Stabilization Pulse' is adjusted to reflect the change in access frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    computational_echo[key] += 1
    divergence_map[key] += 1
    stabilization_pulse[key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the 'Computational Echo' score is initialized based on the current 'Equilibrium Shift', the 'Divergence Map' is updated to include the new entry, and the 'Stabilization Pulse' is set to a neutral state to monitor future access changes.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    computational_echo[key] = INITIAL_ECHO_SCORE + equilibrium_shift
    divergence_map[key] = 0
    stabilization_pulse[key] = NEUTRAL_STABILIZATION_PULSE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the 'Divergence Map' is recalibrated to remove the evicted entry, the 'Stabilization Pulse' is adjusted to reflect the change in cache composition, and the 'Equilibrium Shift' is recalculated to maintain balance between recent and historical access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in divergence_map:
        del divergence_map[evicted_key]
    if evicted_key in stabilization_pulse:
        del stabilization_pulse[evicted_key]
    if evicted_key in computational_echo:
        del computational_echo[evicted_key]
    
    # Recalculate equilibrium shift
    total_accesses = sum(divergence_map.values())
    if total_accesses > 0:
        equilibrium_shift = sum(stabilization_pulse.values()) / total_accesses
    else:
        equilibrium_shift = 0