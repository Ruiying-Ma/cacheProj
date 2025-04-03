# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import math

# Put tunable constant parameters below
INITIAL_BANDWIDTH_ALLOCATION_SCORE = 1.0
BASELINE_ANOMALY_DETECTION_SCORE = 0.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted future access time, bandwidth allocation score, and anomaly detection score for each cache entry.
metadata = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by combining the lowest bandwidth allocation score, highest quantum latency, and anomaly detection score to identify the least valuable and potentially problematic cache entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        score = meta['bandwidth_allocation_score'] - meta['anomaly_detection_score'] + (cache_snapshot.access_count - meta['last_access_time'])
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the last access time to the current time, increments the access frequency, recalculates the predicted future access time based on recent patterns, and adjusts the bandwidth allocation score accordingly.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['last_access_time'] = cache_snapshot.access_count
    meta['access_frequency'] += 1
    meta['predicted_future_access_time'] = cache_snapshot.access_count + (cache_snapshot.access_count - meta['last_access_time']) / meta['access_frequency']
    meta['bandwidth_allocation_score'] = INITIAL_BANDWIDTH_ALLOCATION_SCORE / meta['access_frequency']

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the last access time to the current time, sets the access frequency to one, estimates the predicted future access time, assigns an initial bandwidth allocation score, and sets the anomaly detection score to a baseline value.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    metadata[obj.key] = {
        'last_access_time': cache_snapshot.access_count,
        'access_frequency': 1,
        'predicted_future_access_time': cache_snapshot.access_count + 1,
        'bandwidth_allocation_score': INITIAL_BANDWIDTH_ALLOCATION_SCORE,
        'anomaly_detection_score': BASELINE_ANOMALY_DETECTION_SCORE
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalculates the bandwidth allocation scores for remaining entries to ensure optimal distribution, updates the quantum latency metrics, and re-evaluates the anomaly detection scores to maintain cache integrity.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    del metadata[evicted_obj.key]
    
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        meta['bandwidth_allocation_score'] = INITIAL_BANDWIDTH_ALLOCATION_SCORE / meta['access_frequency']
        meta['anomaly_detection_score'] = BASELINE_ANOMALY_DETECTION_SCORE