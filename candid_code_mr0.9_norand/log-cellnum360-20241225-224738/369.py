# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
SUSTAINABILITY_INCREMENT = 0.1
PREDICTION_UPDATE_FACTOR = 0.1
HARMONIZATION_ADJUSTMENT = 0.05

# Put the metadata specifically maintained by the policy below. The policy maintains a sustainability score for each cache entry, a cross-layer prediction score, and a harmonization index that reflects the balance between cache layers.
sustainability_scores = defaultdict(float)
cross_layer_prediction_scores = defaultdict(float)
harmonization_index = 0.0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on the lowest combined score of sustainability and cross-layer prediction, ensuring that the least sustainable and least predicted useful entries are evicted first.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_combined_score = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (sustainability_scores[key] + 
                          cross_layer_prediction_scores[key])
        if combined_score < min_combined_score:
            min_combined_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the sustainability score is incrementally refined by increasing it slightly, the cross-layer prediction score is updated based on recent access patterns, and the harmonization index is adjusted to reflect the improved balance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    sustainability_scores[obj.key] += SUSTAINABILITY_INCREMENT
    cross_layer_prediction_scores[obj.key] += PREDICTION_UPDATE_FACTOR
    global harmonization_index
    harmonization_index += HARMONIZATION_ADJUSTMENT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the sustainability score is initialized based on initial access frequency, the cross-layer prediction score is set using historical data, and the harmonization index is recalibrated to maintain balance across cache layers.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    sustainability_scores[obj.key] = 1.0  # Initial sustainability score
    cross_layer_prediction_scores[obj.key] = 0.5  # Initial prediction score
    global harmonization_index
    harmonization_index = (harmonization_index + 1) / 2  # Recalibrate

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the sustainability scores of remaining entries are slightly adjusted to reflect the new cache state, the cross-layer prediction scores are recalculated to account for the change, and the harmonization index is updated to ensure continuous balance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    for key in cache_snapshot.cache:
        sustainability_scores[key] *= 0.95  # Slight adjustment
        cross_layer_prediction_scores[key] *= 0.95  # Recalculate prediction

    global harmonization_index
    harmonization_index -= HARMONIZATION_ADJUSTMENT