# Import anything you need below
import time
from collections import defaultdict

# Put tunable constant parameters below
PREDICTION_WEIGHT = 0.5  # Weight for future access time prediction
LOAD_ADJUSTMENT_FACTOR = 0.1  # Factor to adjust prediction based on system load

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, predicted future access time, and current system load. It also tracks synchronization status with real-time data sources to ensure cache consistency.
metadata = {
    'access_frequency': defaultdict(int),
    'last_access_timestamp': {},
    'predicted_future_access_time': {},
    'synchronization_status': defaultdict(bool),
    'system_load': 0
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by considering the lowest predicted future access time, adjusted by current system load. It prioritizes evicting items with low access frequency and those that are not synchronized with real-time data sources.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_predicted_time = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        predicted_time = metadata['predicted_future_access_time'].get(key, float('inf'))
        adjusted_time = predicted_time + metadata['system_load'] * LOAD_ADJUSTMENT_FACTOR
        if (adjusted_time < min_predicted_time or
            (adjusted_time == min_predicted_time and metadata['access_frequency'][key] < metadata['access_frequency'].get(candid_obj_key, float('inf'))) or
            (adjusted_time == min_predicted_time and not metadata['synchronization_status'][key])):
            min_predicted_time = adjusted_time
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency and last access timestamp. It recalculates the predicted future access time using a lightweight predictive model that considers current system load and recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['last_access_timestamp'][key] = cache_snapshot.access_count

    # Recalculate predicted future access time
    recent_access_pattern = metadata['access_frequency'][key]
    metadata['predicted_future_access_time'][key] = (
        PREDICTION_WEIGHT * recent_access_pattern + 
        (1 - PREDICTION_WEIGHT) * metadata['system_load']
    )

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency and last access timestamp. It also predicts the future access time based on initial access patterns and synchronizes the object with real-time data sources if applicable.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_timestamp'][key] = cache_snapshot.access_count

    # Initial prediction of future access time
    metadata['predicted_future_access_time'][key] = (
        PREDICTION_WEIGHT * metadata['access_frequency'][key] + 
        (1 - PREDICTION_WEIGHT) * metadata['system_load']
    )

    # Assume synchronization is done here
    metadata['synchronization_status'][key] = True

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy adjusts the system load metadata to reflect the reduced cache occupancy. It also updates synchronization status to ensure that any dependent real-time data sources are aware of the eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key

    # Adjust system load
    metadata['system_load'] -= evicted_obj.size

    # Update synchronization status
    metadata['synchronization_status'][evicted_key] = False

    # Clean up metadata for evicted object
    del metadata['access_frequency'][evicted_key]
    del metadata['last_access_timestamp'][evicted_key]
    del metadata['predicted_future_access_time'][evicted_key]