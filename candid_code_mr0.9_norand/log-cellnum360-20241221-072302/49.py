# Import anything you need below
import time

# Put tunable constant parameters below
INITIAL_PREDICTIVE_SCORE = 1.0
REAL_TIME_ADJUSTMENT_FACTOR = 0.1
SCORE_INCREMENT = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a predictive score for each cache entry based on historical access patterns, a synchronization timestamp for data streams, and a real-time adjustment factor that adapts to changing usage patterns.
metadata = {
    'predictive_scores': {},  # key: obj.key, value: predictive score
    'sync_timestamps': {},    # key: obj.key, value: last sync timestamp
    'real_time_factor': REAL_TIME_ADJUSTMENT_FACTOR
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache entry with the lowest predictive score, adjusted by the real-time factor, ensuring that less likely accessed items are evicted first while considering recent changes in access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        adjusted_score = metadata['predictive_scores'].get(key, INITIAL_PREDICTIVE_SCORE) * metadata['real_time_factor']
        if adjusted_score < min_score:
            min_score = adjusted_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive score of the accessed entry is increased based on the frequency and recency of access, the synchronization timestamp is updated to reflect the current time, and the real-time adjustment factor is recalibrated to account for the latest usage pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['predictive_scores'][key] = metadata['predictive_scores'].get(key, INITIAL_PREDICTIVE_SCORE) + SCORE_INCREMENT
    metadata['sync_timestamps'][key] = cache_snapshot.access_count
    # Recalibrate real-time factor (simple example, can be more complex)
    metadata['real_time_factor'] = max(0.1, metadata['real_time_factor'] * 0.9)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its predictive score based on initial access predictions, sets the synchronization timestamp to the current time, and adjusts the real-time factor to accommodate the new entry's potential impact on overall cache dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['predictive_scores'][key] = INITIAL_PREDICTIVE_SCORE
    metadata['sync_timestamps'][key] = cache_snapshot.access_count
    # Adjust real-time factor (simple example, can be more complex)
    metadata['real_time_factor'] = min(1.0, metadata['real_time_factor'] * 1.1)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the predictive scores of remaining entries to reflect the removal, updates synchronization timestamps to maintain data stream consistency, and fine-tunes the real-time adjustment factor to optimize future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['predictive_scores']:
        del metadata['predictive_scores'][evicted_key]
    if evicted_key in metadata['sync_timestamps']:
        del metadata['sync_timestamps'][evicted_key]
    
    # Recalibrate predictive scores and real-time factor
    for key in metadata['predictive_scores']:
        metadata['predictive_scores'][key] *= 0.95  # Decay factor for recalibration
    metadata['real_time_factor'] = max(0.1, metadata['real_time_factor'] * 0.95)