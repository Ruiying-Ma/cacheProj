# Import anything you need below
import time

# Put tunable constant parameters below
INITIAL_ALIGNMENT_SCORE = 1.0
DEFAULT_LATENCY_METRIC = 1.0
HEURISTIC_BALANCE_FACTOR = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a predictive alignment score for each cache entry, temporal granularity timestamps, latency metrics for access patterns, and a heuristic balance factor that combines these elements.
metadata = {
    'alignment_scores': {},  # Predictive alignment score for each cache entry
    'temporal_granularity': {},  # Timestamps for each cache entry
    'latency_metrics': {},  # Latency metrics for each cache entry
    'heuristic_balance_factors': {}  # Heuristic balance factor for each cache entry
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest predictive alignment score, adjusted by the heuristic balance factor, while considering entries with outdated temporal granularity and high latency metrics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        alignment_score = metadata['alignment_scores'].get(key, INITIAL_ALIGNMENT_SCORE)
        heuristic_balance = metadata['heuristic_balance_factors'].get(key, HEURISTIC_BALANCE_FACTOR)
        latency_metric = metadata['latency_metrics'].get(key, DEFAULT_LATENCY_METRIC)
        temporal_granularity = metadata['temporal_granularity'].get(key, 0)
        
        # Calculate the effective score for eviction decision
        effective_score = alignment_score / heuristic_balance + latency_metric
        
        # Consider outdated temporal granularity
        if cache_snapshot.access_count - temporal_granularity > 100:  # Example threshold
            effective_score += 10  # Penalize outdated entries
        
        if effective_score < min_score:
            min_score = effective_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive alignment score is increased, temporal granularity is updated to the current timestamp, latency metrics are recalibrated based on the access time, and the heuristic balance factor is adjusted to reflect the improved alignment.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['alignment_scores'][key] = metadata['alignment_scores'].get(key, INITIAL_ALIGNMENT_SCORE) + 1
    metadata['temporal_granularity'][key] = cache_snapshot.access_count
    metadata['latency_metrics'][key] = time.time() - metadata['temporal_granularity'].get(key, 0)
    metadata['heuristic_balance_factors'][key] = metadata['alignment_scores'][key] / (metadata['latency_metrics'][key] + 1)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the predictive alignment score is initialized based on historical data, temporal granularity is set to the current time, latency metrics are initialized to default values, and the heuristic balance factor is calculated to ensure initial balance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['alignment_scores'][key] = INITIAL_ALIGNMENT_SCORE
    metadata['temporal_granularity'][key] = cache_snapshot.access_count
    metadata['latency_metrics'][key] = DEFAULT_LATENCY_METRIC
    metadata['heuristic_balance_factors'][key] = HEURISTIC_BALANCE_FACTOR

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the heuristic balance factor across remaining entries to maintain equilibrium, updates temporal granularity to reflect the change, and adjusts latency metrics to account for the removal of the evicted entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['alignment_scores']:
        del metadata['alignment_scores'][evicted_key]
    if evicted_key in metadata['temporal_granularity']:
        del metadata['temporal_granularity'][evicted_key]
    if evicted_key in metadata['latency_metrics']:
        del metadata['latency_metrics'][evicted_key]
    if evicted_key in metadata['heuristic_balance_factors']:
        del metadata['heuristic_balance_factors'][evicted_key]
    
    # Recalibrate heuristic balance factors for remaining entries
    for key in cache_snapshot.cache.keys():
        metadata['heuristic_balance_factors'][key] = metadata['alignment_scores'][key] / (metadata['latency_metrics'][key] + 1)
        metadata['temporal_granularity'][key] = cache_snapshot.access_count