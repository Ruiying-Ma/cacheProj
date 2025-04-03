# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_TEMPORAL_WEIGHT = 1000
HISTORICAL_ADJUSTMENT_FACTOR = 0.9
TEMPORAL_WEIGHT_INCREMENT = 10

# Put the metadata specifically maintained by the policy below. The policy maintains a frequency counter, a temporal weight score, a historical adjustment factor, and a synthesized cache score for each object. The frequency counter tracks how often an object is accessed, the temporal weight score gives more importance to recent accesses, the historical adjustment factor adjusts the importance of past accesses, and the synthesized cache score combines these elements to determine the object's overall priority.
frequency_counter = defaultdict(int)
temporal_weight_score = defaultdict(lambda: INITIAL_TEMPORAL_WEIGHT)
historical_adjustment_factor = defaultdict(lambda: 1.0)
synthesized_cache_score = defaultdict(float)

def calculate_synthesized_score(key):
    # Invert frequency, apply temporal weight, and adjust with historical factor
    freq = frequency_counter[key]
    temp_weight = temporal_weight_score[key]
    hist_factor = historical_adjustment_factor[key]
    if freq == 0:
        return float('inf')  # Avoid division by zero
    return (1 / freq) * temp_weight * hist_factor

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the object with the lowest synthesized cache score. This score is calculated by inverting the frequency counter, applying the temporal weight, and adjusting with the historical factor to ensure a balanced consideration of both recent and past access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key in cache_snapshot.cache:
        score = calculate_synthesized_score(key)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the frequency counter for the object is incremented, the temporal weight score is increased to reflect the recency of access, and the historical adjustment factor is recalibrated to slightly reduce the impact of older accesses. The synthesized cache score is then recalculated to reflect these updates.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    frequency_counter[key] += 1
    temporal_weight_score[key] += TEMPORAL_WEIGHT_INCREMENT
    historical_adjustment_factor[key] *= HISTORICAL_ADJUSTMENT_FACTOR
    synthesized_cache_score[key] = calculate_synthesized_score(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the frequency counter is initialized to one, the temporal weight score is set to a high initial value to prioritize new entries, and the historical adjustment factor is set to a neutral value. The synthesized cache score is calculated based on these initial values.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    frequency_counter[key] = 1
    temporal_weight_score[key] = INITIAL_TEMPORAL_WEIGHT
    historical_adjustment_factor[key] = 1.0
    synthesized_cache_score[key] = calculate_synthesized_score(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy updates the historical adjustment factor for remaining objects to slightly increase the weight of their past accesses, ensuring that frequently accessed objects maintain their priority. The synthesized cache scores of all remaining objects are recalculated to reflect this adjustment.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        historical_adjustment_factor[key] /= HISTORICAL_ADJUSTMENT_FACTOR
        synthesized_cache_score[key] = calculate_synthesized_score(key)