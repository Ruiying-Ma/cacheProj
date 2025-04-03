# Import anything you need below
import math
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_PREDICTIVE_CONTINUITY_SCORE = 1
DEFAULT_LATENCY_DYNAMIC_FACTOR = 1
ENTROPY_SYNTHESIS_BASE = 1
ADAPTIVE_QUANTUM_BASE = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive continuity score for each cache entry, a latency dynamic factor that tracks access time variations, an entropy synthesis value representing the randomness of access patterns, and an adaptive quantum that adjusts based on recent cache performance.
predictive_continuity_scores = defaultdict(lambda: BASELINE_PREDICTIVE_CONTINUITY_SCORE)
latency_dynamic_factors = defaultdict(lambda: DEFAULT_LATENCY_DYNAMIC_FACTOR)
last_access_times = {}
entropy_synthesis_values = defaultdict(lambda: ENTROPY_SYNTHESIS_BASE)
adaptive_quantum = ADAPTIVE_QUANTUM_BASE

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest predictive continuity score, adjusted by the latency dynamic factor and entropy synthesis value, ensuring that entries with stable and predictable access patterns are retained.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (predictive_continuity_scores[key] * latency_dynamic_factors[key] * 
                 entropy_synthesis_values[key])
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive continuity score of the accessed entry is incremented, the latency dynamic factor is updated based on the time since the last access, and the entropy synthesis value is recalculated to reflect the reduced randomness of the access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    predictive_continuity_scores[key] += 1
    
    current_time = cache_snapshot.access_count
    if key in last_access_times:
        time_since_last_access = current_time - last_access_times[key]
        latency_dynamic_factors[key] = max(1, latency_dynamic_factors[key] - time_since_last_access)
    
    last_access_times[key] = current_time
    
    # Recalculate entropy synthesis value
    entropy_synthesis_values[key] = max(1, entropy_synthesis_values[key] - 1)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the predictive continuity score is initialized to a baseline value, the latency dynamic factor is set to a default state, and the entropy synthesis value is calculated based on the current access pattern, while the adaptive quantum is adjusted to reflect the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    predictive_continuity_scores[key] = BASELINE_PREDICTIVE_CONTINUITY_SCORE
    latency_dynamic_factors[key] = DEFAULT_LATENCY_DYNAMIC_FACTOR
    last_access_times[key] = cache_snapshot.access_count
    
    # Calculate initial entropy synthesis value
    entropy_synthesis_values[key] = ENTROPY_SYNTHESIS_BASE
    
    # Adjust adaptive quantum
    global adaptive_quantum
    adaptive_quantum = max(1, adaptive_quantum - 1)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the adaptive quantum is recalibrated to account for the change in cache composition, and the overall entropy synthesis of the cache is updated to reflect the new access dynamics, ensuring future evictions are more informed.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove metadata for evicted object
    if evicted_key in predictive_continuity_scores:
        del predictive_continuity_scores[evicted_key]
    if evicted_key in latency_dynamic_factors:
        del latency_dynamic_factors[evicted_key]
    if evicted_key in last_access_times:
        del last_access_times[evicted_key]
    if evicted_key in entropy_synthesis_values:
        del entropy_synthesis_values[evicted_key]
    
    # Recalibrate adaptive quantum
    global adaptive_quantum
    adaptive_quantum += 1
    
    # Update overall entropy synthesis
    for key in cache_snapshot.cache:
        entropy_synthesis_values[key] = max(1, entropy_synthesis_values[key] + 1)