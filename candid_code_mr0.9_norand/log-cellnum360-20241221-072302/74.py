# Import anything you need below
import time

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for access frequency
BETA = 0.3   # Weight for temporal coherence score
GAMMA = 0.2  # Weight for last access time

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, and a temporal coherence score for each cache entry. It also tracks global cache access patterns to adaptively adjust eviction thresholds.
cache_metadata = {
    'access_frequency': {},  # Maps obj.key to access frequency
    'last_access_time': {},  # Maps obj.key to last access timestamp
    'temporal_coherence': {},  # Maps obj.key to temporal coherence score
    'global_access_patterns': {
        'total_accesses': 0,
        'total_evictions': 0,
    }
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects a victim for eviction based on a combination of low access frequency, outdated temporal coherence score, and the longest time since last access. It adaptively adjusts the weight of each factor based on recent global access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_freq = cache_metadata['access_frequency'].get(key, 0)
        last_access = cache_metadata['last_access_time'].get(key, 0)
        temporal_score = cache_metadata['temporal_coherence'].get(key, 0)
        
        # Calculate the eviction score
        score = (ALPHA * access_freq) + (BETA * temporal_score) + (GAMMA * (cache_snapshot.access_count - last_access))
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency is incremented, the last access timestamp is updated to the current time, and the temporal coherence score is recalculated based on the time since the last access and recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    cache_metadata['access_frequency'][key] = cache_metadata['access_frequency'].get(key, 0) + 1
    last_access = cache_metadata['last_access_time'].get(key, cache_snapshot.access_count)
    cache_metadata['last_access_time'][key] = cache_snapshot.access_count
    
    # Recalculate temporal coherence score
    time_since_last_access = cache_snapshot.access_count - last_access
    cache_metadata['temporal_coherence'][key] = 1 / (1 + time_since_last_access)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to one, sets the last access timestamp to the current time, and calculates an initial temporal coherence score based on the object's expected lifespan and current access trends.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    cache_metadata['access_frequency'][key] = 1
    cache_metadata['last_access_time'][key] = cache_snapshot.access_count
    cache_metadata['temporal_coherence'][key] = 1  # Initial score, can be adjusted based on trends

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates global access pattern metrics, potentially adjusting the thresholds for access frequency and temporal coherence scores to better align with current usage patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    cache_metadata['global_access_patterns']['total_evictions'] += 1
    # Adjust weights based on global patterns if needed
    # For simplicity, this example does not adjust weights dynamically