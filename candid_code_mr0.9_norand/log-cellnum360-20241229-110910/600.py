# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_FREQUENCY = 1
BASELINE_RECENCY = 0

# Put the metadata specifically maintained by the policy below. The policy maintains a statistical profile for each cache entry, including access frequency, recency, and a differential encoding of access patterns. It also keeps a distilled summary of global cache access trends to calibrate strategic decisions.
cache_metadata = {
    'frequency': defaultdict(lambda: BASELINE_FREQUENCY),
    'recency': defaultdict(lambda: BASELINE_RECENCY),
    'differential_encoding': defaultdict(int),
    'global_trend_summary': {
        'total_accesses': 0,
        'total_hits': 0,
        'total_misses': 0
    }
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects a victim by evaluating entries against a statistical continuum, prioritizing those with low access frequency and recency scores. It uses differential encoding to identify entries with redundant access patterns, and strategic calibration to align eviction with global access trends.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        frequency = cache_metadata['frequency'][key]
        recency = cache_metadata['recency'][key]
        differential = cache_metadata['differential_encoding'][key]
        
        # Calculate a score based on frequency, recency, and differential encoding
        score = frequency + recency + differential
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency and recency scores of the entry. It recalibrates the differential encoding to reflect the latest access pattern and adjusts the global trend summary to incorporate the hit.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    cache_metadata['frequency'][key] += 1
    cache_metadata['recency'][key] = cache_snapshot.access_count
    cache_metadata['differential_encoding'][key] += 1  # Simplified differential encoding update
    cache_metadata['global_trend_summary']['total_hits'] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its statistical profile with baseline frequency and recency scores. It encodes the initial access pattern and updates the global trend summary to reflect the new entry's potential impact.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    cache_metadata['frequency'][key] = BASELINE_FREQUENCY
    cache_metadata['recency'][key] = cache_snapshot.access_count
    cache_metadata['differential_encoding'][key] = 0  # Initial differential encoding
    cache_metadata['global_trend_summary']['total_accesses'] += 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the statistical profile of the evicted entry. It recalibrates the global trend summary to account for the removal and adjusts strategic calibration parameters to refine future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in cache_metadata['frequency']:
        del cache_metadata['frequency'][evicted_key]
    if evicted_key in cache_metadata['recency']:
        del cache_metadata['recency'][evicted_key]
    if evicted_key in cache_metadata['differential_encoding']:
        del cache_metadata['differential_encoding'][evicted_key]
    
    cache_metadata['global_trend_summary']['total_accesses'] -= 1