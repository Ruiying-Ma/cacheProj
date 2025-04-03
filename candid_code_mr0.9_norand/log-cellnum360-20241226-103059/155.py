# Import anything you need below
import math
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_PREDICTIVE_METRIC = 1.0
INITIAL_ENTROPY_SCORE = 1.0
PHASE_SHIFT_THRESHOLD = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains a loop counter for each data item, a predictive metric based on access patterns, an entropy score to measure randomness of access, and a phase shift indicator to track changes in access patterns.
metadata = {
    'loop_counter': defaultdict(int),
    'predictive_metric': defaultdict(lambda: INITIAL_PREDICTIVE_METRIC),
    'entropy_score': defaultdict(lambda: INITIAL_ENTROPY_SCORE),
    'phase_shift_indicator': defaultdict(float)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the item with the highest entropy score, indicating the least predictable access pattern, and the lowest predictive metric, suggesting it is least likely to be accessed soon.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_entropy = -1
    min_predictive_metric = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        entropy = metadata['entropy_score'][key]
        predictive_metric = metadata['predictive_metric'][key]
        
        if entropy > max_entropy or (entropy == max_entropy and predictive_metric < min_predictive_metric):
            max_entropy = entropy
            min_predictive_metric = predictive_metric
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the loop counter for the accessed item is incremented, the predictive metric is updated based on recent access patterns, and the entropy score is recalculated to reflect the new access information.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['loop_counter'][key] += 1
    
    # Update predictive metric
    metadata['predictive_metric'][key] = 1 / (1 + metadata['loop_counter'][key])
    
    # Recalculate entropy score
    metadata['entropy_score'][key] = -math.log(metadata['predictive_metric'][key])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the loop counter is initialized, the predictive metric is set based on initial access predictions, the entropy score is calculated, and the phase shift indicator is set to detect any immediate changes in access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['loop_counter'][key] = 0
    metadata['predictive_metric'][key] = INITIAL_PREDICTIVE_METRIC
    metadata['entropy_score'][key] = INITIAL_ENTROPY_SCORE
    metadata['phase_shift_indicator'][key] = PHASE_SHIFT_THRESHOLD

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the predictive metrics and entropy scores of remaining items to account for the removal, and adjusts the phase shift indicators to ensure they reflect the current access dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['loop_counter']:
        del metadata['loop_counter'][evicted_key]
        del metadata['predictive_metric'][evicted_key]
        del metadata['entropy_score'][evicted_key]
        del metadata['phase_shift_indicator'][evicted_key]
    
    # Recalibrate remaining items
    for key in cache_snapshot.cache:
        metadata['phase_shift_indicator'][key] *= 0.9  # Example adjustment