# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
PREDICTIVE_SCORE_INIT = 1.0
DYNAMIC_CONSISTENCY_NEUTRAL = 1.0
LOAD_ADAPTATION_FACTOR_INIT = 1.0
TEMPORAL_FUSION_INDEX_INIT = 0.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a predictive score for each cache entry based on access patterns, a dynamic consistency score reflecting the stability of these patterns, a load adaptation factor indicating current system load, and a temporal fusion index that combines recent access recency and frequency.
metadata = {
    'predictive_score': defaultdict(lambda: PREDICTIVE_SCORE_INIT),
    'dynamic_consistency': defaultdict(lambda: DYNAMIC_CONSISTENCY_NEUTRAL),
    'load_adaptation_factor': LOAD_ADAPTATION_FACTOR_INIT,
    'temporal_fusion_index': defaultdict(lambda: TEMPORAL_FUSION_INDEX_INIT)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest combined score of predictive allocation and temporal fusion, adjusted by the dynamic consistency and load adaptation factors to ensure optimal performance under varying conditions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (
            metadata['predictive_score'][key] +
            metadata['temporal_fusion_index'][key] -
            metadata['dynamic_consistency'][key] * metadata['load_adaptation_factor']
        )
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive score is increased based on the access pattern, the dynamic consistency score is adjusted to reflect the stability of this pattern, the load adaptation factor is recalibrated if system load has changed, and the temporal fusion index is updated to reflect the recent access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['predictive_score'][key] += 1
    metadata['dynamic_consistency'][key] *= 1.1  # Example adjustment
    metadata['temporal_fusion_index'][key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the predictive score is initialized based on initial access predictions, the dynamic consistency score is set to a neutral value, the load adaptation factor is adjusted to account for the new entry, and the temporal fusion index is initialized to reflect the insertion time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['predictive_score'][key] = PREDICTIVE_SCORE_INIT
    metadata['dynamic_consistency'][key] = DYNAMIC_CONSISTENCY_NEUTRAL
    metadata['temporal_fusion_index'][key] = cache_snapshot.access_count
    metadata['load_adaptation_factor'] *= 1.05  # Example adjustment

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the predictive scores of remaining entries are recalibrated to reflect the change in cache composition, the dynamic consistency scores are adjusted to maintain stability, the load adaptation factor is updated to reflect the reduced load, and the temporal fusion indices are recalculated to ensure temporal relevance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del metadata['predictive_score'][evicted_key]
    del metadata['dynamic_consistency'][evicted_key]
    del metadata['temporal_fusion_index'][evicted_key]
    
    for key in cache_snapshot.cache:
        metadata['predictive_score'][key] *= 0.95  # Example recalibration
        metadata['dynamic_consistency'][key] *= 0.98  # Example adjustment
    
    metadata['load_adaptation_factor'] *= 0.95  # Example adjustment