# Import anything you need below
import math

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for predictive accuracy
BETA = 0.3   # Weight for temporal alignment
GAMMA = 0.2  # Weight for normalized access frequency

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted future access time, and normalized access patterns for each cache entry.
metadata = {
    'access_frequency': {},  # {key: frequency}
    'last_access_time': {},  # {key: last_access_time}
    'predicted_future_access_time': {},  # {key: predicted_future_access_time}
    'normalized_access_frequency': {}  # {key: normalized_access_frequency}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by combining predictive accuracy of future accesses, temporal alignment with recent access patterns, and normalized access frequency, prioritizing entries with the lowest combined score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        predictive_accuracy = metadata['predicted_future_access_time'].get(key, float('inf'))
        temporal_alignment = cache_snapshot.access_count - metadata['last_access_time'].get(key, 0)
        normalized_access_frequency = metadata['normalized_access_frequency'].get(key, 0)
        
        score = (ALPHA * predictive_accuracy) + (BETA * temporal_alignment) + (GAMMA * normalized_access_frequency)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency by incrementing it, records the current time as the last access time, refines the predicted future access time based on recent patterns, and normalizes the access frequency across all entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predicted_future_access_time'][key] = cache_snapshot.access_count + 1  # Simplified prediction
    
    total_frequency = sum(metadata['access_frequency'].values())
    for k in metadata['access_frequency']:
        metadata['normalized_access_frequency'][k] = metadata['access_frequency'][k] / total_frequency

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency to 1, sets the current time as the last access time, predicts the future access time based on initial patterns, and normalizes the access frequency across all entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predicted_future_access_time'][key] = cache_snapshot.access_count + 1  # Simplified prediction
    
    total_frequency = sum(metadata['access_frequency'].values())
    for k in metadata['access_frequency']:
        metadata['normalized_access_frequency'][k] = metadata['access_frequency'][k] / total_frequency

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalculates the normalized access frequencies for the remaining entries and refines the predictive model based on the eviction decision to improve future accuracy.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['last_access_time']:
        del metadata['last_access_time'][evicted_key]
    if evicted_key in metadata['predicted_future_access_time']:
        del metadata['predicted_future_access_time'][evicted_key]
    if evicted_key in metadata['normalized_access_frequency']:
        del metadata['normalized_access_frequency'][evicted_key]
    
    total_frequency = sum(metadata['access_frequency'].values())
    for k in metadata['access_frequency']:
        metadata['normalized_access_frequency'][k] = metadata['access_frequency'][k] / total_frequency