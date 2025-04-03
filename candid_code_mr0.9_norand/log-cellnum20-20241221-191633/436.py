# Import anything you need below
import time

# Put tunable constant parameters below
INITIAL_SYNC_GAP = 0
INITIAL_PREDICTIVE_SCALING = 1.0
INITIAL_ELASTIC_CONTINUITY = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a synchronization gap counter for each cache entry, a predictive scaling factor based on access patterns, an elastic continuity score reflecting the temporal distribution of accesses, and a timestamp of the last access.
metadata = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the highest synchronization gap counter, adjusted by the predictive scaling factor and elastic continuity score, prioritizing entries with the least recent access timestamp.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_score = float('-inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        score = (meta['sync_gap'] * meta['predictive_scaling'] * meta['elastic_continuity'])
        
        if score > max_score or (score == max_score and meta['last_access'] < metadata[candid_obj_key]['last_access']):
            max_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the synchronization gap counter is reset, the predictive scaling factor is adjusted based on the frequency of recent accesses, the elastic continuity score is updated to reflect the temporal distribution, and the last access timestamp is refreshed.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    meta = metadata[key]
    
    # Reset synchronization gap counter
    meta['sync_gap'] = INITIAL_SYNC_GAP
    
    # Adjust predictive scaling factor
    meta['predictive_scaling'] *= 1.1  # Example adjustment
    
    # Update elastic continuity score
    meta['elastic_continuity'] *= 1.05  # Example adjustment
    
    # Refresh last access timestamp
    meta['last_access'] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the synchronization gap counter is initialized, the predictive scaling factor is set based on initial access predictions, the elastic continuity score is calculated from initial temporal distribution assumptions, and the last access timestamp is set to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata[key] = {
        'sync_gap': INITIAL_SYNC_GAP,
        'predictive_scaling': INITIAL_PREDICTIVE_SCALING,
        'elastic_continuity': INITIAL_ELASTIC_CONTINUITY,
        'last_access': cache_snapshot.access_count
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the synchronization gap counters of remaining entries are incremented, the predictive scaling factors are recalibrated to reflect the new cache state, and the elastic continuity scores are adjusted to account for the change in temporal distribution.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        
        # Increment synchronization gap counter
        meta['sync_gap'] += 1
        
        # Recalibrate predictive scaling factor
        meta['predictive_scaling'] *= 0.95  # Example recalibration
        
        # Adjust elastic continuity score
        meta['elastic_continuity'] *= 0.98  # Example adjustment
    
    # Remove metadata for evicted object
    if evicted_obj.key in metadata:
        del metadata[evicted_obj.key]