# Import anything you need below
import collections

# Put tunable constant parameters below
DEFAULT_ACCESS_FREQUENCY = 1
DEFAULT_LATENCY_SENSITIVITY = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted future access time, and latency sensitivity score for each cache entry. It also tracks global adaptive metrics such as average access latency and cache hit rate.
metadata = collections.defaultdict(lambda: {
    'access_frequency': DEFAULT_ACCESS_FREQUENCY,
    'last_access_time': 0,
    'predicted_future_access_time': 0,
    'latency_sensitivity': DEFAULT_LATENCY_SENSITIVITY
})

global_metrics = {
    'average_access_latency': 0,
    'cache_hit_rate': 0
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by calculating a composite score for each entry, which combines its predicted future access time, latency sensitivity, and access frequency. The entry with the lowest score is chosen for eviction, balancing immediate need and future access predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        score = (meta['predicted_future_access_time'] * meta['latency_sensitivity']) / meta['access_frequency']
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the last access time and increments the access frequency for the entry. It also recalculates the predicted future access time using a predictive queuing model and adjusts the latency sensitivity score based on recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['last_access_time'] = cache_snapshot.access_count
    meta['access_frequency'] += 1
    # Recalculate predicted future access time (simplified as a function of access frequency)
    meta['predicted_future_access_time'] = cache_snapshot.access_count + (1 / meta['access_frequency'])
    # Adjust latency sensitivity score (simplified as a function of access frequency)
    meta['latency_sensitivity'] = 1.0 / meta['access_frequency']

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its metadata with a default access frequency, sets the last access time to the current time, estimates the predicted future access time using historical data, and assigns an initial latency sensitivity score based on object type.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    metadata[obj.key] = {
        'access_frequency': DEFAULT_ACCESS_FREQUENCY,
        'last_access_time': cache_snapshot.access_count,
        'predicted_future_access_time': cache_snapshot.access_count + 1,
        'latency_sensitivity': DEFAULT_LATENCY_SENSITIVITY
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy updates global adaptive metrics, such as recalculating the average access latency and adjusting the cache hit rate. It also refines the predictive model parameters based on the evicted entry's metadata to improve future predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Update global metrics
    total_accesses = cache_snapshot.hit_count + cache_snapshot.miss_count
    if total_accesses > 0:
        global_metrics['cache_hit_rate'] = cache_snapshot.hit_count / total_accesses
    
    # Remove metadata of evicted object
    if evicted_obj.key in metadata:
        del metadata[evicted_obj.key]