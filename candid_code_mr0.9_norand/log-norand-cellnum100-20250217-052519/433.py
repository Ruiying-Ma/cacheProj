# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import time

# Put tunable constant parameters below
PREDICTIVE_SCORE_WEIGHT = 0.7
LAST_ACCESS_TIME_WEIGHT = 0.3

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, and a predictive score derived from a machine learning model that forecasts future access patterns based on historical data.
metadata = {
    'access_frequency': {},  # {obj.key: frequency}
    'last_access_time': {},  # {obj.key: last_access_time}
    'predictive_score': {}   # {obj.key: predictive_score}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by combining the predictive score with temporal dynamics, prioritizing items with lower predicted future access and older last access times.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (PREDICTIVE_SCORE_WEIGHT * metadata['predictive_score'][key] +
                          LAST_ACCESS_TIME_WEIGHT * (cache_snapshot.access_count - metadata['last_access_time'][key]))
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency, refreshes the last access time, and recalculates the predictive score using the machine learning model to reflect the latest access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predictive_score'][key] = calculate_predictive_score(obj)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency, sets the current time as the last access time, and computes an initial predictive score based on the object's characteristics and historical data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predictive_score'][key] = calculate_predictive_score(obj)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the metadata associated with the evicted object and may adjust the machine learning model parameters to improve future predictive accuracy based on the eviction outcome.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    del metadata['access_frequency'][key]
    del metadata['last_access_time'][key]
    del metadata['predictive_score'][key]

def calculate_predictive_score(obj):
    '''
    This function calculates the predictive score for an object based on its characteristics and historical data.
    - Args:
        - `obj`: The object for which the predictive score is to be calculated.
    - Return:
        - `score`: The calculated predictive score.
    '''
    # Placeholder for a machine learning model to predict future access patterns
    # For simplicity, we use a dummy function here
    return obj.size * 0.1  # Example: predictive score based on object size