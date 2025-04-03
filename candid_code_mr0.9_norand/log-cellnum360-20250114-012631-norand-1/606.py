# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import time

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQUENCY = 0.4
WEIGHT_LAST_ACCESS_TIME = 0.3
WEIGHT_CONTEXT_RELEVANCE = 0.2
WEIGHT_PREDICTED_FUTURE_ACCESS = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, data context (e.g., user behavior, location), and predicted future access patterns using machine learning models.
metadata = {
    'access_frequency': {},
    'last_access_time': {},
    'context_relevance': {},
    'predicted_future_access': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by evaluating a weighted score combining low access frequency, old last access time, low relevance in current context, and low predicted future access probability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_frequency = metadata['access_frequency'].get(key, 0)
        last_access_time = metadata['last_access_time'].get(key, 0)
        context_relevance = metadata['context_relevance'].get(key, 0)
        predicted_future_access = metadata['predicted_future_access'].get(key, 0)
        
        score = (WEIGHT_ACCESS_FREQUENCY * access_frequency +
                 WEIGHT_LAST_ACCESS_TIME * (cache_snapshot.access_count - last_access_time) +
                 WEIGHT_CONTEXT_RELEVANCE * context_relevance +
                 WEIGHT_PREDICTED_FUTURE_ACCESS * predicted_future_access)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency by incrementing it, refreshes the last access time to the current time, and re-evaluates the data context and future access prediction based on the latest information.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    # Re-evaluate context relevance and future access prediction
    metadata['context_relevance'][key] = evaluate_context_relevance(obj)
    metadata['predicted_future_access'][key] = predict_future_access(obj)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access time to the current time, and assesses the data context and future access prediction using the initial context and predictive models.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['context_relevance'][key] = evaluate_context_relevance(obj)
    metadata['predicted_future_access'][key] = predict_future_access(obj)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy rebalances the weights used for eviction decisions based on the success of the prediction model, and updates the context-aware optimization parameters to improve future eviction choices.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Rebalance weights based on the success of the prediction model
    # This is a placeholder for the actual rebalancing logic
    # For simplicity, we assume the weights remain constant in this example
    pass

def evaluate_context_relevance(obj):
    # Placeholder function to evaluate context relevance
    # In a real implementation, this would use actual context data
    return 0

def predict_future_access(obj):
    # Placeholder function to predict future access probability
    # In a real implementation, this would use a machine learning model
    return 0