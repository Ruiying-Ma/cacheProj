# Import anything you need below
import time

# Put tunable constant parameters below
PREDICTION_FACTOR = 1.0  # Factor to adjust predicted future access time
ADAPTIVE_SCORE_FACTOR = 0.1  # Factor to adjust adaptive metric score

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, predicted future access time using a quantum efficiency model, and an adaptive metric score that adjusts based on system load and access patterns.
metadata = {
    'access_frequency': {},  # Maps object key to access frequency
    'last_access_timestamp': {},  # Maps object key to last access timestamp
    'predicted_future_access_time': {},  # Maps object key to predicted future access time
    'adaptive_metric_score': 1.0  # Global adaptive metric score
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache entry, which combines the inverse of access frequency, the time since last access, and the predicted future access time. The entry with the highest composite score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_score = -1

    for key, cached_obj in cache_snapshot.cache.items():
        access_freq = metadata['access_frequency'].get(key, 1)
        last_access = metadata['last_access_timestamp'].get(key, cache_snapshot.access_count)
        predicted_future = metadata['predicted_future_access_time'].get(key, 0)

        # Calculate composite score
        score = (1 / access_freq) + (cache_snapshot.access_count - last_access) + (predicted_future * PREDICTION_FACTOR)

        if score > max_score:
            max_score = score
            candid_obj_key = key

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency is incremented, the last access timestamp is updated to the current time, and the predicted future access time is recalibrated using the quantum efficiency model to reflect the latest access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_timestamp'][key] = cache_snapshot.access_count
    # Recalibrate predicted future access time
    metadata['predicted_future_access_time'][key] = (metadata['predicted_future_access_time'].get(key, 0) + cache_snapshot.access_count) / 2

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the access frequency is initialized to one, the last access timestamp is set to the current time, and the predicted future access time is calculated using initial access patterns and system load metrics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_timestamp'][key] = cache_snapshot.access_count
    # Initial predicted future access time
    metadata['predicted_future_access_time'][key] = cache_snapshot.access_count + (cache_snapshot.capacity / obj.size)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the adaptive metric score is adjusted to reflect the current system load and access patterns, ensuring that future evictions are more aligned with the dynamic behavior of the system.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Adjust adaptive metric score
    load_factor = cache_snapshot.size / cache_snapshot.capacity
    metadata['adaptive_metric_score'] *= (1 + ADAPTIVE_SCORE_FACTOR * (1 - load_factor))