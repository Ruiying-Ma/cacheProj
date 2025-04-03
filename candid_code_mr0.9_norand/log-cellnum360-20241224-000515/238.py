# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_PREDICTIVE_SCORE = 1.0
INITIAL_DYNAMIC_PRIORITY = 1.0
INITIAL_LOAD_EFFICIENCY = 1.0
DEFAULT_ADAPTIVE_BUFFER = 1.0
PREDICTIVE_SCORE_INCREMENT = 0.1
DYNAMIC_PRIORITY_INCREMENT = 0.1
LOAD_EFFICIENCY_DECREMENT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a predictive score for each cache entry based on historical access patterns, an adaptive buffer size for each entry, a dynamic priority level, and a load efficiency metric that tracks the resource cost of accessing each entry.
metadata = {
    'predictive_score': defaultdict(lambda: INITIAL_PREDICTIVE_SCORE),
    'adaptive_buffer': defaultdict(lambda: DEFAULT_ADAPTIVE_BUFFER),
    'dynamic_priority': defaultdict(lambda: INITIAL_DYNAMIC_PRIORITY),
    'load_efficiency': defaultdict(lambda: INITIAL_LOAD_EFFICIENCY)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest combined score of predictive analysis, dynamic priority, and load efficiency, while considering the adaptive buffer to ensure frequently accessed items are retained longer.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_combined_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (
            metadata['predictive_score'][key] +
            metadata['dynamic_priority'][key] +
            metadata['load_efficiency'][key]
        ) / metadata['adaptive_buffer'][key]
        
        if combined_score < min_combined_score:
            min_combined_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive score is increased based on the frequency and recency of access, the dynamic priority is adjusted upwards, and the load efficiency is recalculated to reflect the reduced cost of future accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['predictive_score'][key] += PREDICTIVE_SCORE_INCREMENT
    metadata['dynamic_priority'][key] += DYNAMIC_PRIORITY_INCREMENT
    metadata['load_efficiency'][key] = max(
        metadata['load_efficiency'][key] - LOAD_EFFICIENCY_DECREMENT, 0.1
    )

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the predictive score is initialized based on initial access predictions, the adaptive buffer is set to a default size, the dynamic priority is set to a baseline level, and the load efficiency is calculated based on the initial access cost.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['predictive_score'][key] = INITIAL_PREDICTIVE_SCORE
    metadata['adaptive_buffer'][key] = DEFAULT_ADAPTIVE_BUFFER
    metadata['dynamic_priority'][key] = INITIAL_DYNAMIC_PRIORITY
    metadata['load_efficiency'][key] = INITIAL_LOAD_EFFICIENCY

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy recalibrates the predictive scores of remaining entries to reflect the changed cache state, adjusts the adaptive buffer sizes if necessary, and updates the dynamic priorities to ensure optimal future evictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        metadata['predictive_score'][key] *= 0.9  # Example recalibration
        metadata['dynamic_priority'][key] *= 0.9  # Example recalibration
        # Adjust adaptive buffer if necessary
        if metadata['adaptive_buffer'][key] > 1.0:
            metadata['adaptive_buffer'][key] *= 0.95