# Import anything you need below
import time

# Put tunable constant parameters below
IMPORTANCE_SCORE_INITIAL = 1
RESOURCE_USAGE_INITIAL = 1
LATENCY_IMPACT_INITIAL = 1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, data importance score, and predictive access patterns. It also tracks resource usage and latency impact for each cached item.
metadata = {
    'access_frequency': {},
    'last_access_time': {},
    'importance_score': {},
    'predictive_access_pattern': {},
    'resource_usage': {},
    'latency_impact': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a weighted score combining low access frequency, old last access time, low data importance score, and low predicted future access. Items with higher resource usage and higher latency impact are deprioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (
            metadata['access_frequency'][key] * 0.1 +
            (cache_snapshot.access_count - metadata['last_access_time'][key]) * 0.3 +
            metadata['importance_score'][key] * 0.2 +
            metadata['predictive_access_pattern'][key] * 0.4
        )
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency by incrementing it, refreshes the last access time to the current time, and adjusts the predictive access pattern based on recent access trends. The data importance score is recalculated if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    # Adjust predictive access pattern and recalculate importance score if necessary
    metadata['predictive_access_pattern'][key] = (metadata['predictive_access_pattern'][key] + 1) / 2
    # Recalculate importance score if necessary (this is a placeholder, actual calculation may vary)
    metadata['importance_score'][key] = IMPORTANCE_SCORE_INITIAL

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access time to the current time, assigns an initial data importance score based on predefined criteria, and starts tracking predictive access patterns. Resource usage and latency impact are also recorded.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['importance_score'][key] = IMPORTANCE_SCORE_INITIAL
    metadata['predictive_access_pattern'][key] = 1
    metadata['resource_usage'][key] = RESOURCE_USAGE_INITIAL
    metadata['latency_impact'][key] = LATENCY_IMPACT_INITIAL

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes all associated metadata for the evicted item and recalculates resource usage and latency impact for the remaining items to ensure optimal cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Remove metadata for the evicted item
    del metadata['access_frequency'][evicted_key]
    del metadata['last_access_time'][evicted_key]
    del metadata['importance_score'][evicted_key]
    del metadata['predictive_access_pattern'][evicted_key]
    del metadata['resource_usage'][evicted_key]
    del metadata['latency_impact'][evicted_key]
    
    # Recalculate resource usage and latency impact for remaining items if necessary
    # This is a placeholder, actual recalculation logic may vary
    for key in cache_snapshot.cache:
        metadata['resource_usage'][key] = RESOURCE_USAGE_INITIAL
        metadata['latency_impact'][key] = LATENCY_IMPACT_INITIAL