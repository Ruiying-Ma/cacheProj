# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
DEFAULT_RECURSIVE_LATENCY = 1.0
DEFAULT_DYNAMIC_THRESHOLD = 1.0
DEFAULT_PREDICTIVE_SCORE = 1.0
DEFAULT_TEMPORAL_DRIFT = 0.0
LATENCY_DECAY = 0.9
THRESHOLD_ADJUSTMENT = 0.1
PREDICTIVE_SCORE_INCREMENT = 0.1
TEMPORAL_DRIFT_DECREMENT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry including recursive latency (average time taken for repeated accesses), a dynamic threshold (adjusted based on access patterns), a predictive score (forecasting future accesses), and a temporal drift factor (tracking changes in access frequency over time).
metadata = defaultdict(lambda: {
    'recursive_latency': DEFAULT_RECURSIVE_LATENCY,
    'dynamic_threshold': DEFAULT_DYNAMIC_THRESHOLD,
    'predictive_score': DEFAULT_PREDICTIVE_SCORE,
    'temporal_drift': DEFAULT_TEMPORAL_DRIFT
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying entries with the highest temporal drift and lowest predictive score, ensuring that entries with increasing latency and decreasing access likelihood are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    max_drift = -float('inf')
    min_predictive_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        obj_metadata = metadata[key]
        if (obj_metadata['temporal_drift'] > max_drift or
            (obj_metadata['temporal_drift'] == max_drift and obj_metadata['predictive_score'] < min_predictive_score)):
            max_drift = obj_metadata['temporal_drift']
            min_predictive_score = obj_metadata['predictive_score']
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the recursive latency is recalculated to reflect the new access time, the dynamic threshold is adjusted based on the current access pattern, the predictive score is increased to reflect the likelihood of future accesses, and the temporal drift is decreased to indicate stable access frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    obj_metadata = metadata[obj.key]
    obj_metadata['recursive_latency'] *= LATENCY_DECAY
    obj_metadata['dynamic_threshold'] += THRESHOLD_ADJUSTMENT
    obj_metadata['predictive_score'] += PREDICTIVE_SCORE_INCREMENT
    obj_metadata['temporal_drift'] -= TEMPORAL_DRIFT_DECREMENT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the recursive latency is initialized to a default value, the dynamic threshold is set based on initial access patterns, the predictive score is calculated using initial access predictions, and the temporal drift is set to a neutral value indicating no prior access history.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    metadata[obj.key] = {
        'recursive_latency': DEFAULT_RECURSIVE_LATENCY,
        'dynamic_threshold': DEFAULT_DYNAMIC_THRESHOLD,
        'predictive_score': DEFAULT_PREDICTIVE_SCORE,
        'temporal_drift': DEFAULT_TEMPORAL_DRIFT
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the dynamic threshold is recalibrated to reflect the new cache state, the predictive integration model is updated to improve future predictions, and the temporal drift is adjusted to account for the removal of the evicted entry's access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    del metadata[evicted_obj.key]
    for key in metadata:
        metadata[key]['dynamic_threshold'] -= THRESHOLD_ADJUSTMENT
        metadata[key]['temporal_drift'] += TEMPORAL_DRIFT_DECREMENT