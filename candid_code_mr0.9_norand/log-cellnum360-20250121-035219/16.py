# Import anything you need below
import collections

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQUENCY = 0.4
WEIGHT_RECENCY = 0.3
WEIGHT_SPATIAL_LOCALITY = 0.2
WEIGHT_COHERENCE_STATE = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency, spatial locality patterns, coherence state, and prefetching hints. It also tracks adaptive thresholds for replacement decisions.
metadata = {
    'access_frequency': collections.defaultdict(int),
    'recency': collections.defaultdict(int),
    'spatial_locality': collections.defaultdict(int),
    'coherence_state': collections.defaultdict(int),
    'prefetching_hints': collections.defaultdict(list),
    'adaptive_thresholds': {
        'frequency_threshold': 1,
        'recency_threshold': 1,
        'locality_threshold': 1,
        'coherence_threshold': 1
    }
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a weighted score combining low access frequency, old recency, poor spatial locality, and coherence state. It dynamically adjusts weights based on recent cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (WEIGHT_ACCESS_FREQUENCY * metadata['access_frequency'][key] +
                 WEIGHT_RECENCY * (cache_snapshot.access_count - metadata['recency'][key]) +
                 WEIGHT_SPATIAL_LOCALITY * metadata['spatial_locality'][key] +
                 WEIGHT_COHERENCE_STATE * metadata['coherence_state'][key])
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency and recency of the accessed object. It also refines spatial locality patterns and adjusts coherence state if necessary. Prefetching hints are updated based on access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    metadata['access_frequency'][obj.key] += 1
    metadata['recency'][obj.key] = cache_snapshot.access_count
    # Update spatial locality patterns and coherence state if necessary
    # Update prefetching hints based on access patterns

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency and recency. It updates spatial locality patterns and coherence state. Prefetching hints are generated based on the object's address and surrounding data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    metadata['access_frequency'][obj.key] = 1
    metadata['recency'][obj.key] = cache_snapshot.access_count
    # Initialize spatial locality patterns and coherence state
    # Generate prefetching hints based on the object's address and surrounding data

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalibrates adaptive thresholds based on the evicted object's metadata. It updates spatial locality patterns and coherence state to reflect the removal. Prefetching hints are adjusted to avoid redundant prefetches.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Recalibrate adaptive thresholds based on the evicted object's metadata
    # Update spatial locality patterns and coherence state to reflect the removal
    # Adjust prefetching hints to avoid redundant prefetches