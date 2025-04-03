# Import anything you need below
import time
from collections import defaultdict

# Put tunable constant parameters below
ANOMALY_SCORE_DECAY = 0.9
FUTURE_ACCESS_PREDICTION_DECAY = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, predicted future access patterns, and anomaly scores for each cache entry. It also tracks overall cache performance metrics and resource usage trends.
metadata = {
    'access_frequency': defaultdict(int),
    'last_access_timestamp': {},
    'predicted_future_access': defaultdict(float),
    'anomaly_scores': defaultdict(float),
    'cache_performance_metrics': {
        'total_accesses': 0,
        'total_hits': 0,
        'total_misses': 0,
    },
    'resource_usage_trends': {
        'current_size': 0,
        'capacity': 0,
    }
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying entries with low predicted future access and high anomaly scores, while also considering the overall cache performance benchmark. It aims to maintain adaptive resilience by isolating anomalies and ensuring resource efficiency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        future_access = metadata['predicted_future_access'][key]
        anomaly_score = metadata['anomaly_scores'][key]
        score = future_access - anomaly_score
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency and last access timestamp for the entry. It also recalculates the predicted future access pattern and adjusts the anomaly score based on recent access behavior.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['last_access_timestamp'][key] = cache_snapshot.access_count
    
    # Update predicted future access pattern
    metadata['predicted_future_access'][key] = (
        FUTURE_ACCESS_PREDICTION_DECAY * metadata['predicted_future_access'][key] +
        (1 - FUTURE_ACCESS_PREDICTION_DECAY) * metadata['access_frequency'][key]
    )
    
    # Adjust anomaly score
    metadata['anomaly_scores'][key] *= ANOMALY_SCORE_DECAY

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency and last access timestamp. It forecasts the resource impact of the new entry and updates the overall cache performance metrics to reflect the change.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_timestamp'][key] = cache_snapshot.access_count
    metadata['predicted_future_access'][key] = 1.0
    metadata['anomaly_scores'][key] = 0.0
    
    # Update cache performance metrics
    metadata['cache_performance_metrics']['total_accesses'] = cache_snapshot.access_count
    metadata['cache_performance_metrics']['total_hits'] = cache_snapshot.hit_count
    metadata['cache_performance_metrics']['total_misses'] = cache_snapshot.miss_count
    
    # Update resource usage trends
    metadata['resource_usage_trends']['current_size'] = cache_snapshot.size
    metadata['resource_usage_trends']['capacity'] = cache_snapshot.capacity

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the cache performance benchmark and resource usage trends. It also adjusts the anomaly isolation parameters to improve future eviction decisions and maintain adaptive resilience.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Recalibrate cache performance benchmark
    metadata['cache_performance_metrics']['total_accesses'] = cache_snapshot.access_count
    metadata['cache_performance_metrics']['total_hits'] = cache_snapshot.hit_count
    metadata['cache_performance_metrics']['total_misses'] = cache_snapshot.miss_count
    
    # Update resource usage trends
    metadata['resource_usage_trends']['current_size'] = cache_snapshot.size
    metadata['resource_usage_trends']['capacity'] = cache_snapshot.capacity
    
    # Adjust anomaly isolation parameters
    evicted_key = evicted_obj.key
    metadata['anomaly_scores'][evicted_key] = 0.0