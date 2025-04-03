# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_PATTERN = 1.0
MODERATE_SIGNAL_STRENGTH = 5.0
NEUTRAL_DATA_ASSIMILATION_INDEX = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a differential encoding of access patterns, algorithmic complexity scores for each cache entry, and a signal strength indicator derived from recent access frequency and recency. It also includes a data assimilation index that reflects the integration of new data into existing patterns.
differential_encoding = defaultdict(lambda: BASELINE_PATTERN)
signal_strength = defaultdict(lambda: MODERATE_SIGNAL_STRENGTH)
data_assimilation_index = defaultdict(lambda: NEUTRAL_DATA_ASSIMILATION_INDEX)
algorithmic_complexity = defaultdict(lambda: 1.0)  # Example complexity score

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest combined score of signal strength and data assimilation index, while considering the algorithmic complexity to ensure minimal disruption to cache efficiency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (signal_strength[key] + data_assimilation_index[key]) / algorithmic_complexity[key]
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the differential encoding is updated to reflect the new access pattern, the signal strength is increased to indicate recent access, and the data assimilation index is adjusted to integrate the new access into the existing pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    differential_encoding[key] += 1
    signal_strength[key] += 1
    data_assimilation_index[key] += 0.5

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the differential encoding with a baseline pattern, assigns a moderate signal strength, and sets the data assimilation index to a neutral value to allow for rapid adaptation.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    differential_encoding[key] = BASELINE_PATTERN
    signal_strength[key] = MODERATE_SIGNAL_STRENGTH
    data_assimilation_index[key] = NEUTRAL_DATA_ASSIMILATION_INDEX

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the differential encoding to remove the evicted pattern, decreases the overall signal strength to reflect reduced cache capacity, and adjusts the data assimilation index to account for the loss of integrated data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in differential_encoding:
        del differential_encoding[evicted_key]
    if evicted_key in signal_strength:
        del signal_strength[evicted_key]
    if evicted_key in data_assimilation_index:
        del data_assimilation_index[evicted_key]
    
    # Decrease overall signal strength to reflect reduced cache capacity
    for key in signal_strength:
        signal_strength[key] *= 0.9  # Example reduction factor