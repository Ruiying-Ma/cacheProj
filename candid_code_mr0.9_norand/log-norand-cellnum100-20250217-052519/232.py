# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import time
from collections import defaultdict

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQUENCY = 0.4
WEIGHT_LAST_ACCESS_TIME = 0.4
WEIGHT_CLUSTER_RELEVANCE = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, contextual tags (e.g., user behavior patterns), and cluster identifiers derived from hierarchical clustering of access patterns.
metadata = {
    'access_frequency': defaultdict(int),
    'last_access_time': {},
    'contextual_tags': {},
    'cluster_identifiers': {},
    'predictive_weights': {
        'access_frequency': WEIGHT_ACCESS_FREQUENCY,
        'last_access_time': WEIGHT_LAST_ACCESS_TIME,
        'cluster_relevance': WEIGHT_CLUSTER_RELEVANCE
    }
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by dynamically prioritizing objects based on a weighted score that combines low access frequency, old last access time, and low relevance within its cluster. Predictive learning adjusts weights based on historical eviction success.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_frequency = metadata['access_frequency'][key]
        last_access_time = metadata['last_access_time'][key]
        cluster_relevance = metadata['cluster_identifiers'][key]
        
        score = (metadata['predictive_weights']['access_frequency'] * access_frequency +
                 metadata['predictive_weights']['last_access_time'] * (cache_snapshot.access_count - last_access_time) +
                 metadata['predictive_weights']['cluster_relevance'] * cluster_relevance)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency by incrementing it, refreshes the last access time to the current time, and re-evaluates the object's cluster relevance using contextual analysis.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    # Re-evaluate cluster relevance (dummy implementation)
    metadata['cluster_identifiers'][key] = 1  # Placeholder for actual cluster relevance calculation

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency to 1, sets the last access time to the current time, assigns contextual tags based on initial access context, and places it in a cluster using hierarchical clustering.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['contextual_tags'][key] = 'initial_context'  # Placeholder for actual contextual tags
    metadata['cluster_identifiers'][key] = 1  # Placeholder for actual cluster assignment

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes its metadata, re-adjusts the cluster compositions if necessary, and updates the predictive learning model with the outcome to refine future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del metadata['access_frequency'][evicted_key]
    del metadata['last_access_time'][evicted_key]
    del metadata['contextual_tags'][evicted_key]
    del metadata['cluster_identifiers'][evicted_key]
    # Update predictive learning model (dummy implementation)
    # Placeholder for actual predictive learning model update