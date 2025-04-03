# Import anything you need below
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
import numpy as np

# Put tunable constant parameters below
CROSS_VALIDATION_FOLDS = 5

# Put the metadata specifically maintained by the policy below. The policy maintains a metadata structure that includes access frequency, recency of access, and a nonlinear regression model score for each cache entry. Additionally, it keeps a hyperparameter set that is tuned using cross-validation to optimize the ensemble model's prediction accuracy.
metadata = {
    'access_frequency': {},  # {key: frequency}
    'recency': {},           # {key: last_access_time}
    'regression_scores': {}, # {key: regression_score}
    'model': LinearRegression(),
    'hyperparameters': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy uses an ensemble model combining access frequency, recency, and nonlinear regression scores to predict the least valuable cache entry. The entry with the lowest predicted value is chosen as the eviction victim.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_value = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        frequency = metadata['access_frequency'].get(key, 0)
        recency = metadata['recency'].get(key, 0)
        regression_score = metadata['regression_scores'].get(key, 0)
        
        # Ensemble model prediction (simple weighted sum for demonstration)
        predicted_value = frequency * 0.3 + recency * 0.3 + regression_score * 0.4
        
        if predicted_value < min_value:
            min_value = predicted_value
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency is incremented, the recency is updated to the current time, and the nonlinear regression model is retrained using the updated data point. The ensemble model is then recalibrated using the new regression score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['recency'][key] = cache_snapshot.access_count
    
    # Update regression model
    X = np.array([[metadata['access_frequency'][k], metadata['recency'][k]] for k in cache_snapshot.cache.keys()])
    y = np.array([metadata['regression_scores'].get(k, 0) for k in cache_snapshot.cache.keys()])
    
    if len(X) > 1:  # Ensure there is enough data to train
        metadata['model'].fit(X, y)
        metadata['regression_scores'][key] = metadata['model'].predict([[metadata['access_frequency'][key], metadata['recency'][key]]])[0]

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency and recency metadata. The nonlinear regression model is updated to include the new entry, and the ensemble model is adjusted to incorporate the new regression score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['recency'][key] = cache_snapshot.access_count
    
    # Update regression model
    X = np.array([[metadata['access_frequency'][k], metadata['recency'][k]] for k in cache_snapshot.cache.keys()])
    y = np.array([metadata['regression_scores'].get(k, 0) for k in cache_snapshot.cache.keys()])
    
    if len(X) > 1:  # Ensure there is enough data to train
        metadata['model'].fit(X, y)
        metadata['regression_scores'][key] = metadata['model'].predict([[metadata['access_frequency'][key], metadata['recency'][key]]])[0]

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the metadata of the evicted entry. It then performs hyperparameter tuning using cross-validation to ensure the ensemble model remains optimized for the current cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    metadata['access_frequency'].pop(evicted_key, None)
    metadata['recency'].pop(evicted_key, None)
    metadata['regression_scores'].pop(evicted_key, None)
    
    # Hyperparameter tuning using cross-validation
    X = np.array([[metadata['access_frequency'][k], metadata['recency'][k]] for k in cache_snapshot.cache.keys()])
    y = np.array([metadata['regression_scores'].get(k, 0) for k in cache_snapshot.cache.keys()])
    
    if len(X) > 1:  # Ensure there is enough data to train
        scores = cross_val_score(metadata['model'], X, y, cv=CROSS_VALIDATION_FOLDS)
        metadata['hyperparameters']['cv_score'] = np.mean(scores)