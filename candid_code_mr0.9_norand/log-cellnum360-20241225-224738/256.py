# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_FREQUENCY = 1
BASELINE_RECENCY = 1
PREDICTIVE_SCORE_WEIGHT = 0.5
GLOBAL_CONTEXT_ADJUSTMENT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a hierarchical structure of metadata, including access frequency, recency, and a predictive score for each cache entry. It also tracks a global context score that adapts based on workload patterns.
metadata = {
    'access_frequency': defaultdict(lambda: BASELINE_FREQUENCY),
    'recency': defaultdict(lambda: BASELINE_RECENCY),
    'predictive_score': defaultdict(float),
    'global_context_score': 1.0
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects a victim by evaluating a composite score derived from the entry's access frequency, recency, and predictive score, adjusted by the global context score. The entry with the lowest composite score is chosen for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        frequency = metadata['access_frequency'][key]
        recency = metadata['recency'][key]
        predictive_score = metadata['predictive_score'][key]
        
        composite_score = (frequency + recency + predictive_score) * metadata['global_context_score']
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency and recency of the entry are incremented, and the predictive score is adjusted based on the current global context score to reflect anticipated future accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['predictive_score'][key] += PREDICTIVE_SCORE_WEIGHT * metadata['global_context_score']

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency and recency to baseline values and calculates an initial predictive score using the global context score to estimate its future access likelihood.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = BASELINE_FREQUENCY
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['predictive_score'][key] = PREDICTIVE_SCORE_WEIGHT * metadata['global_context_score']

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the global context score is updated to reflect the change in cache composition, and the predictive scores of remaining entries are recalibrated to align with the new context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Update global context score
    metadata['global_context_score'] += GLOBAL_CONTEXT_ADJUSTMENT
    
    # Recalibrate predictive scores
    for key in cache_snapshot.cache:
        metadata['predictive_score'][key] *= metadata['global_context_score']