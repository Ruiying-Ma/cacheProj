# Import anything you need below
import time

# Put tunable constant parameters below
INITIAL_PREDICTIVE_SCORE = 1.0
NEUTRAL_FEEDBACK_SCORE = 0.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access timestamps, access frequency, a predictive score for future accesses, and a feedback score indicating the accuracy of past predictions.
metadata = {
    'access_timestamps': {},  # {obj.key: timestamp}
    'access_frequencies': {},  # {obj.key: frequency}
    'predictive_scores': {},  # {obj.key: predictive_score}
    'feedback_scores': {}  # {obj.key: feedback_score}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a combination of the lowest predictive score and the lowest feedback score, prioritizing items that are both predicted to be accessed less frequently and have had inaccurate past predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        predictive_score = metadata['predictive_scores'].get(key, INITIAL_PREDICTIVE_SCORE)
        feedback_score = metadata['feedback_scores'].get(key, NEUTRAL_FEEDBACK_SCORE)
        combined_score = predictive_score + feedback_score
        
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access timestamp and access frequency for the item are updated. The predictive score is adjusted based on the new access pattern, and the feedback score is updated to reflect the accuracy of the previous prediction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Update access timestamp and frequency
    metadata['access_timestamps'][key] = current_time
    metadata['access_frequencies'][key] = metadata['access_frequencies'].get(key, 0) + 1
    
    # Adjust predictive score (simple example: inverse of frequency)
    metadata['predictive_scores'][key] = 1.0 / metadata['access_frequencies'][key]
    
    # Update feedback score (simple example: difference between predicted and actual access)
    last_access_time = metadata['access_timestamps'].get(key, current_time)
    actual_interval = current_time - last_access_time
    predicted_interval = 1.0 / metadata['predictive_scores'][key]
    metadata['feedback_scores'][key] = abs(predicted_interval - actual_interval)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access timestamp to the current time, sets the access frequency to one, assigns an initial predictive score based on temporal estimation, and sets a neutral feedback score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Initialize metadata
    metadata['access_timestamps'][key] = current_time
    metadata['access_frequencies'][key] = 1
    metadata['predictive_scores'][key] = INITIAL_PREDICTIVE_SCORE
    metadata['feedback_scores'][key] = NEUTRAL_FEEDBACK_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an item, the policy updates the feedback scores of remaining items to reflect the accuracy of the prediction model, and recalibrates the predictive scores based on the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove metadata of evicted object
    if evicted_key in metadata['access_timestamps']:
        del metadata['access_timestamps'][evicted_key]
    if evicted_key in metadata['access_frequencies']:
        del metadata['access_frequencies'][evicted_key]
    if evicted_key in metadata['predictive_scores']:
        del metadata['predictive_scores'][evicted_key]
    if evicted_key in metadata['feedback_scores']:
        del metadata['feedback_scores'][evicted_key]
    
    # Recalibrate predictive scores and update feedback scores for remaining items
    for key in cache_snapshot.cache:
        frequency = metadata['access_frequencies'].get(key, 1)
        metadata['predictive_scores'][key] = 1.0 / frequency
        last_access_time = metadata['access_timestamps'].get(key, cache_snapshot.access_count)
        actual_interval = cache_snapshot.access_count - last_access_time
        predicted_interval = 1.0 / metadata['predictive_scores'][key]
        metadata['feedback_scores'][key] = abs(predicted_interval - actual_interval)