# Import anything you need below
import heapq

# Put tunable constant parameters below
SYMBIOTIC_TUNING_FACTOR = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a harmonic frequency score for each cache entry, a sequential inversion index, a cognitive overlay map of access patterns, and a symbiotic tuning factor that adjusts based on cache performance.
harmonic_frequency_scores = {}
sequential_inversion_index = {}
cognitive_overlay_map = {}
symbiotic_tuning_factor = SYMBIOTIC_TUNING_FACTOR

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest harmonic frequency score, adjusted by the symbiotic tuning factor, and cross-referenced with the cognitive overlay map to ensure minimal disruption to predicted access patterns.
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
        score = harmonic_frequency_scores.get(key, 0) * symbiotic_tuning_factor
        if score < min_score:
            min_score = score
            candid_obj_key = key
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the harmonic frequency score of the accessed entry is incremented, the sequential inversion index is updated to reflect the new access order, and the cognitive overlay map is refined to enhance prediction accuracy.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    harmonic_frequency_scores[key] = harmonic_frequency_scores.get(key, 0) + 1
    sequential_inversion_index[key] = cache_snapshot.access_count
    cognitive_overlay_map[key] = cognitive_overlay_map.get(key, 0) + 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its harmonic frequency score and sequential inversion index, updates the cognitive overlay map to incorporate the new entry, and adjusts the symbiotic tuning factor to reflect the current cache dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    harmonic_frequency_scores[key] = 1
    sequential_inversion_index[key] = cache_snapshot.access_count
    cognitive_overlay_map[key] = 1
    symbiotic_tuning_factor = SYMBIOTIC_TUNING_FACTOR * (cache_snapshot.hit_count / (cache_snapshot.hit_count + cache_snapshot.miss_count))

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the harmonic frequency scores of remaining entries, updates the sequential inversion index to close the gap left by the evicted entry, and refines the cognitive overlay map to account for the change in cache composition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in harmonic_frequency_scores:
        del harmonic_frequency_scores[evicted_key]
    if evicted_key in sequential_inversion_index:
        del sequential_inversion_index[evicted_key]
    if evicted_key in cognitive_overlay_map:
        del cognitive_overlay_map[evicted_key]
    
    # Recalibrate scores and indices
    for key in cache_snapshot.cache:
        harmonic_frequency_scores[key] *= symbiotic_tuning_factor
        cognitive_overlay_map[key] = cognitive_overlay_map.get(key, 0) * symbiotic_tuning_factor