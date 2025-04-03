# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
import heapq
from collections import defaultdict, deque

# Put tunable constant parameters below
LATENCY_WEIGHT = 0.5
FREQUENCY_WEIGHT = 0.3
TIME_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted future access time, and data latency metrics for each cached object. It also keeps a queue of asynchronous events related to cache operations.
metadata = {
    'access_frequency': defaultdict(int),
    'last_access_time': {},
    'predicted_future_access_time': {},
    'data_latency': {},
    'async_events': deque()
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy uses a predictive model to forecast future access patterns and data latency. It selects the eviction victim based on a combination of the least likely to be accessed soon and the highest data latency, ensuring minimal impact on performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_freq = metadata['access_frequency'][key]
        last_access = metadata['last_access_time'][key]
        predicted_future_access = metadata['predicted_future_access_time'][key]
        data_latency = metadata['data_latency'][key]
        
        score = (LATENCY_WEIGHT * data_latency +
                 FREQUENCY_WEIGHT * (1 / (access_freq + 1)) +
                 TIME_WEIGHT * (cache_snapshot.access_count - last_access))
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency and last access time of the object. It also recalculates the predicted future access time using the predictive model and adjusts the data latency metrics accordingly.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    # Predictive model update (simplified as current time + some constant)
    metadata['predicted_future_access_time'][key] = cache_snapshot.access_count + 100
    # Adjust data latency metrics (simplified as a constant value)
    metadata['data_latency'][key] = 10

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency, sets the current time as the last access time, and uses the predictive model to estimate its future access time. It also records initial data latency metrics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    # Predictive model initialization (simplified as current time + some constant)
    metadata['predicted_future_access_time'][key] = cache_snapshot.access_count + 100
    # Initial data latency metrics (simplified as a constant value)
    metadata['data_latency'][key] = 10

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the metadata of the evicted object and updates the queue of asynchronous events to reflect the change. It also recalibrates the predictive model based on the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Remove metadata of the evicted object
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['last_access_time']:
        del metadata['last_access_time'][evicted_key]
    if evicted_key in metadata['predicted_future_access_time']:
        del metadata['predicted_future_access_time'][evicted_key]
    if evicted_key in metadata['data_latency']:
        del metadata['data_latency'][evicted_key]
    
    # Update the queue of asynchronous events
    metadata['async_events'].append((cache_snapshot.access_count, 'evict', evicted_key))
    
    # Recalibrate the predictive model (simplified as no-op for this example)