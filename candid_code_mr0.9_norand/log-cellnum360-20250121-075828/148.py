# Import anything you need below
import math

# Put tunable constant parameters below
INITIAL_ADAPTIVE_QUANTUM = 1.0
ENTROPY_DECAY_FACTOR = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access timestamps, access frequencies, adaptive quantum values for each cache entry, and a predictive entropy score that estimates the likelihood of future accesses.
metadata = {
    'timestamps': {},  # {obj.key: last_access_time}
    'frequencies': {},  # {obj.key: access_frequency}
    'adaptive_quantum': {},  # {obj.key: adaptive_quantum_value}
    'entropy_scores': {}  # {obj.key: predictive_entropy_score}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache entry based on its temporal coherence, adaptive quantum value, and predictive entropy. The entry with the lowest composite score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        temporal_coherence = cache_snapshot.access_count - metadata['timestamps'][key]
        adaptive_quantum = metadata['adaptive_quantum'][key]
        entropy_score = metadata['entropy_scores'][key]
        
        composite_score = temporal_coherence * adaptive_quantum * entropy_score
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access timestamp and frequency for the accessed entry are updated. The adaptive quantum value is recalibrated based on recent access patterns, and the predictive entropy score is adjusted to reflect the increased likelihood of future accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['timestamps'][key] = cache_snapshot.access_count
    metadata['frequencies'][key] += 1
    metadata['adaptive_quantum'][key] = 1 / metadata['frequencies'][key]
    metadata['entropy_scores'][key] *= ENTROPY_DECAY_FACTOR

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access timestamp to the current time, sets the access frequency to one, assigns an initial adaptive quantum value based on heuristic analysis, and calculates an initial predictive entropy score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['timestamps'][key] = cache_snapshot.access_count
    metadata['frequencies'][key] = 1
    metadata['adaptive_quantum'][key] = INITIAL_ADAPTIVE_QUANTUM
    metadata['entropy_scores'][key] = 1.0  # Initial entropy score

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the adaptive quantum values and predictive entropy scores of the remaining entries to ensure they reflect the current cache state and access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['timestamps']:
        del metadata['timestamps'][evicted_key]
        del metadata['frequencies'][evicted_key]
        del metadata['adaptive_quantum'][evicted_key]
        del metadata['entropy_scores'][evicted_key]
    
    for key in cache_snapshot.cache:
        metadata['adaptive_quantum'][key] = 1 / metadata['frequencies'][key]
        metadata['entropy_scores'][key] *= ENTROPY_DECAY_FACTOR