# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import collections

# Put tunable constant parameters below
WEIGHT_INVERSE_ACCESS_FREQ = 0.5
WEIGHT_TIME_SINCE_LAST_ACCESS = 0.3
WEIGHT_COHERENCE_SCORE = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, and a coherence score for each cache line. The coherence score is calculated based on the number of invalidations and updates received from other caches in the system.
metadata = collections.defaultdict(lambda: {'access_freq': 0, 'last_access_time': 0, 'coherence_score': 0})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache line, which is a weighted sum of the inverse of access frequency, the time since last access, and the coherence score. The cache line with the highest composite score is chosen for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_composite_score = -float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_freq = metadata[key]['access_freq']
        last_access_time = metadata[key]['last_access_time']
        coherence_score = metadata[key]['coherence_score']
        
        inverse_access_freq = 1 / access_freq if access_freq > 0 else float('inf')
        time_since_last_access = cache_snapshot.access_count - last_access_time
        
        composite_score = (WEIGHT_INVERSE_ACCESS_FREQ * inverse_access_freq +
                           WEIGHT_TIME_SINCE_LAST_ACCESS * time_since_last_access +
                           WEIGHT_COHERENCE_SCORE * coherence_score)
        
        if composite_score > max_composite_score:
            max_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the access frequency is incremented, the last access time is updated to the current time, and the coherence score is adjusted based on any recent coherence traffic related to the cache line.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata[key]['access_freq'] += 1
    metadata[key]['last_access_time'] = cache_snapshot.access_count
    # Adjust coherence score based on recent coherence traffic (this is a placeholder)
    metadata[key]['coherence_score'] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object into the cache, the access frequency is initialized to 1, the last access time is set to the current time, and the coherence score is initialized based on the initial coherence state of the object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata[key]['access_freq'] = 1
    metadata[key]['last_access_time'] = cache_snapshot.access_count
    # Initialize coherence score based on initial coherence state (this is a placeholder)
    metadata[key]['coherence_score'] = 0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the metadata for the evicted cache line is cleared. The coherence scores of remaining cache lines are adjusted to reflect the removal of the evicted line, and the access frequencies and last access times are recalibrated if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del metadata[evicted_key]
    
    # Adjust coherence scores of remaining cache lines (this is a placeholder)
    for key in cache_snapshot.cache:
        metadata[key]['coherence_score'] -= 1