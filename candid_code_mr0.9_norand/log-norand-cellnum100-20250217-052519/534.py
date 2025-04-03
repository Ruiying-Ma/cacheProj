# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import collections

# Put tunable constant parameters below
INITIAL_USAGE_FREQUENCY = 1

# Put the metadata specifically maintained by the policy below. The policy maintains an efficiency matrix that tracks the access patterns and usage frequency of cached objects, a predictive model that forecasts future access probabilities, and a real-time analytics component that monitors and updates these metrics continuously.
efficiency_matrix = collections.defaultdict(int)
predictive_model = collections.defaultdict(float)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the object with the lowest predicted future access probability, as determined by the predictive model, and cross-referenced with the efficiency matrix to ensure minimal impact on overall cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_predicted_access_prob = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        predicted_access_prob = predictive_model[key]
        if predicted_access_prob < min_predicted_access_prob:
            min_predicted_access_prob = predicted_access_prob
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the efficiency matrix to reflect the increased usage frequency of the accessed object and refines the predictive model using real-time analytics to improve future access predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    efficiency_matrix[key] += 1
    predictive_model[key] = efficiency_matrix[key] / cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy updates the efficiency matrix to include the new object with an initial usage frequency, and the predictive model is adjusted to account for the new object's potential future access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    efficiency_matrix[key] = INITIAL_USAGE_FREQUENCY
    predictive_model[key] = INITIAL_USAGE_FREQUENCY / cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the evicted object from the efficiency matrix and recalibrates the predictive model to exclude the evicted object, ensuring that future predictions remain accurate and relevant.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in efficiency_matrix:
        del efficiency_matrix[evicted_key]
    if evicted_key in predictive_model:
        del predictive_model[evicted_key]