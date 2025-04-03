# Import anything you need below
import math

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.5
TIME_WEIGHT = 0.3
HEURISTIC_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted future access time using predictive interpolation, and a heuristic score derived from dynamic coherence and temporal insights.
metadata = {
    'access_frequency': {},  # Maps obj.key to access frequency
    'last_access_time': {},  # Maps obj.key to last access time
    'predicted_future_access_time': {},  # Maps obj.key to predicted future access time
    'heuristic_score': {}  # Maps obj.key to heuristic score
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache entry, which combines the predicted future access time, access frequency, and heuristic score. The entry with the lowest composite score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        frequency = metadata['access_frequency'].get(key, 0)
        last_access = metadata['last_access_time'].get(key, 0)
        predicted_future = metadata['predicted_future_access_time'].get(key, float('inf'))
        heuristic = metadata['heuristic_score'].get(key, 0)
        
        composite_score = (FREQUENCY_WEIGHT * frequency +
                           TIME_WEIGHT * (cache_snapshot.access_count - last_access) +
                           HEURISTIC_WEIGHT * heuristic)
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the last access time to the current time, increments the access frequency, and recalculates the heuristic score using dynamic coherence and temporal insights.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    # Recalculate heuristic score (example calculation)
    metadata['heuristic_score'][key] = math.log(metadata['access_frequency'][key] + 1)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the last access time to the current time, sets the access frequency to one, and computes an initial heuristic score based on predicted future access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['access_frequency'][key] = 1
    # Initial heuristic score (example calculation)
    metadata['heuristic_score'][key] = 1.0
    # Predicted future access time (example prediction)
    metadata['predicted_future_access_time'][key] = cache_snapshot.access_count + 100

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy adjusts the heuristic mapping for remaining entries to reflect the change in cache dynamics and recalibrates predictive interpolation parameters to improve future predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Remove metadata for evicted object
    metadata['access_frequency'].pop(evicted_key, None)
    metadata['last_access_time'].pop(evicted_key, None)
    metadata['predicted_future_access_time'].pop(evicted_key, None)
    metadata['heuristic_score'].pop(evicted_key, None)
    
    # Adjust heuristic scores for remaining entries (example adjustment)
    for key in cache_snapshot.cache:
        metadata['heuristic_score'][key] *= 0.9  # Example adjustment factor