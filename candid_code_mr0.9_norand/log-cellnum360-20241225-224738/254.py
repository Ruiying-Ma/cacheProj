# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
COHERENCE_THRESHOLD = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains a real-time index for each cache entry, which includes a fusion score derived from access frequency, recency, and data coherence metrics. It also tracks a global coherence score to ensure consistency across cache entries.
cache_metadata = {
    'access_frequency': defaultdict(int),
    'recency': {},
    'coherence': defaultdict(float),
    'fusion_score': {},
    'global_coherence_score': 0.0
}

def calculate_fusion_score(key):
    # Calculate the fusion score based on access frequency, recency, and coherence
    frequency = cache_metadata['access_frequency'][key]
    recency = cache_metadata['recency'][key]
    coherence = cache_metadata['coherence'][key]
    return frequency + recency + coherence

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim based on the lowest fusion score, prioritizing entries with low access frequency, older recency, and poor coherence. It ensures that the global coherence score remains above a predefined threshold.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_fusion_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        fusion_score = cache_metadata['fusion_score'][key]
        if fusion_score < min_fusion_score:
            min_fusion_score = fusion_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the access frequency and updates the recency timestamp of the accessed entry. It recalculates the fusion score and adjusts the global coherence score to reflect the improved consistency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    cache_metadata['access_frequency'][key] += 1
    cache_metadata['recency'][key] = cache_snapshot.access_count
    cache_metadata['fusion_score'][key] = calculate_fusion_score(key)
    # Adjust global coherence score
    cache_metadata['global_coherence_score'] += 0.01  # Example adjustment

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its real-time index with default values, calculates an initial fusion score, and updates the global coherence score to incorporate the new entry's impact on overall cache consistency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    cache_metadata['access_frequency'][key] = 1
    cache_metadata['recency'][key] = cache_snapshot.access_count
    cache_metadata['coherence'][key] = 0.5  # Initial coherence value
    cache_metadata['fusion_score'][key] = calculate_fusion_score(key)
    # Update global coherence score
    cache_metadata['global_coherence_score'] += 0.01  # Example adjustment

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the real-time index of the evicted entry, recalculates the global coherence score to account for the removal, and adjusts the fusion scores of remaining entries if necessary to maintain balance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Remove the real-time index of the evicted entry
    del cache_metadata['access_frequency'][evicted_key]
    del cache_metadata['recency'][evicted_key]
    del cache_metadata['coherence'][evicted_key]
    del cache_metadata['fusion_score'][evicted_key]
    
    # Recalculate global coherence score
    cache_metadata['global_coherence_score'] -= 0.01  # Example adjustment
    
    # Adjust fusion scores of remaining entries if necessary
    for key in cache_snapshot.cache:
        cache_metadata['fusion_score'][key] = calculate_fusion_score(key)