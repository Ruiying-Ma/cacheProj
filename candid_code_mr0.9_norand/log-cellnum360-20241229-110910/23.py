# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_PREDICTIVE_SCORE = 1.0
INITIAL_ERROR_CORRECTION = 0.0
FREQUENCY_WEIGHT = 0.5
RECENCY_WEIGHT = 0.5
ERROR_CORRECTION_ADJUSTMENT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive score for each cache entry, a harmonized data index that combines access frequency and recency, a dynamic index for tracking changes in access patterns, and an error correction factor to adjust predictions based on past inaccuracies.
predictive_scores = defaultdict(lambda: INITIAL_PREDICTIVE_SCORE)
harmonized_data_index = defaultdict(lambda: 0)
dynamic_index = defaultdict(lambda: 0)
error_correction_factor = defaultdict(lambda: INITIAL_ERROR_CORRECTION)
access_frequency = defaultdict(lambda: 0)
last_access_time = defaultdict(lambda: 0)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest predictive score, adjusted by the error correction factor, ensuring that entries with stable access patterns are less likely to be evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = predictive_scores[key] + error_correction_factor[key]
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive score is recalibrated using recent access data, the harmonized data index is updated to reflect increased recency and frequency, the dynamic index is adjusted to capture any shifts in access patterns, and the error correction factor is refined based on the accuracy of the prediction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] += 1
    last_access_time[key] = cache_snapshot.access_count
    
    # Recalculate harmonized data index
    harmonized_data_index[key] = (FREQUENCY_WEIGHT * access_frequency[key] +
                                  RECENCY_WEIGHT * (cache_snapshot.access_count - last_access_time[key]))
    
    # Adjust predictive score
    predictive_scores[key] = harmonized_data_index[key] + dynamic_index[key]
    
    # Refine error correction factor
    error_correction_factor[key] -= ERROR_CORRECTION_ADJUSTMENT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the predictive score is initialized based on initial access predictions, the harmonized data index is set to reflect the object's initial access characteristics, the dynamic index is initialized to track future changes, and the error correction factor is set to a neutral value.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] = 1
    last_access_time[key] = cache_snapshot.access_count
    
    # Initialize harmonized data index
    harmonized_data_index[key] = FREQUENCY_WEIGHT + RECENCY_WEIGHT
    
    # Initialize predictive score
    predictive_scores[key] = harmonized_data_index[key]
    
    # Initialize dynamic index
    dynamic_index[key] = 0
    
    # Set error correction factor to neutral
    error_correction_factor[key] = INITIAL_ERROR_CORRECTION

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the predictive scores of remaining entries are recalibrated to account for the removal, the harmonized data index is adjusted to reflect the new cache state, the dynamic index is updated to capture any resulting shifts in access patterns, and the error correction factor is updated to improve future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove metadata for evicted object
    del predictive_scores[evicted_key]
    del harmonized_data_index[evicted_key]
    del dynamic_index[evicted_key]
    del error_correction_factor[evicted_key]
    del access_frequency[evicted_key]
    del last_access_time[evicted_key]
    
    # Recalibrate predictive scores and update indices for remaining entries
    for key in cache_snapshot.cache:
        harmonized_data_index[key] = (FREQUENCY_WEIGHT * access_frequency[key] +
                                      RECENCY_WEIGHT * (cache_snapshot.access_count - last_access_time[key]))
        predictive_scores[key] = harmonized_data_index[key] + dynamic_index[key]
        error_correction_factor[key] += ERROR_CORRECTION_ADJUSTMENT