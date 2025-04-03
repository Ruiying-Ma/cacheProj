# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import math

# Put tunable constant parameters below
INITIAL_PREDICTIVE_SCORE = 0.5
INITIAL_ANOMALY_SCORE = 0.0
STOCHASTIC_GRADIENT_STEP = 0.01
ANOMALY_THRESHOLD = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency, and a predictive score for each cache entry. It also tracks anomaly scores to detect unusual access patterns and uses stochastic gradient values to adjust predictive scores dynamically.
metadata = {
    'access_frequency': {},
    'recency': {},
    'predictive_score': {},
    'anomaly_score': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by combining the predictive score and anomaly score. Entries with low predictive scores and high anomaly scores are prioritized for eviction. If scores are similar, the least recently used entry is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        predictive_score = metadata['predictive_score'].get(key, INITIAL_PREDICTIVE_SCORE)
        anomaly_score = metadata['anomaly_score'].get(key, INITIAL_ANOMALY_SCORE)
        combined_score = predictive_score - anomaly_score
        
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
        elif combined_score == min_score:
            if metadata['recency'].get(key, 0) < metadata['recency'].get(candid_obj_key, 0):
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency and recency of the entry are updated. The predictive score is adjusted using a stochastic gradient based on the hit, and the anomaly score is recalculated to reflect the new access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['recency'][key] = cache_snapshot.access_count
    
    # Update predictive score using stochastic gradient
    predictive_score = metadata['predictive_score'].get(key, INITIAL_PREDICTIVE_SCORE)
    metadata['predictive_score'][key] = predictive_score + STOCHASTIC_GRADIENT_STEP
    
    # Recalculate anomaly score
    access_frequency = metadata['access_frequency'][key]
    anomaly_score = math.log(1 + access_frequency) - predictive_score
    metadata['anomaly_score'][key] = anomaly_score

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency and recency. The predictive score is set using initial hyperparameters, and the anomaly score is calculated based on the initial access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['predictive_score'][key] = INITIAL_PREDICTIVE_SCORE
    metadata['anomaly_score'][key] = INITIAL_ANOMALY_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy recalibrates the predictive hyperparameters and anomaly detection thresholds. It also updates the stochastic gradient values to improve future predictions and adjusts data regularization parameters to maintain cache stability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['recency']:
        del metadata['recency'][evicted_key]
    if evicted_key in metadata['predictive_score']:
        del metadata['predictive_score'][evicted_key]
    if evicted_key in metadata['anomaly_score']:
        del metadata['anomaly_score'][evicted_key]
    
    # Recalibrate predictive hyperparameters and anomaly detection thresholds
    # This is a placeholder for more complex recalibration logic
    for key in metadata['predictive_score']:
        metadata['predictive_score'][key] = max(0, metadata['predictive_score'][key] - STOCHASTIC_GRADIENT_STEP)
    for key in metadata['anomaly_score']:
        metadata['anomaly_score'][key] = max(0, metadata['anomaly_score'][key] - ANOMALY_THRESHOLD)