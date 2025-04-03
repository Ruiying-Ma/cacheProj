# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
PREDICTIVE_BUFFER_INIT = 1.0
DYNAMIC_SYNTHESIS_NEUTRAL = 1.0
LATENCY_MODULATION_INIT = 1.0
TEMPORAL_GRANULARITY_INIT = 0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a predictive buffer score for each cache entry, a dynamic synthesis index that adjusts based on access patterns, a latency modulation factor that accounts for the time sensitivity of data, and a temporal granularity counter that tracks the frequency of access over time.
metadata = {
    'predictive_buffer': defaultdict(lambda: PREDICTIVE_BUFFER_INIT),
    'dynamic_synthesis': defaultdict(lambda: DYNAMIC_SYNTHESIS_NEUTRAL),
    'latency_modulation': defaultdict(lambda: LATENCY_MODULATION_INIT),
    'temporal_granularity': defaultdict(lambda: TEMPORAL_GRANULARITY_INIT),
    'last_access_time': defaultdict(int)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache entry with the lowest combined score of predictive buffer, dynamic synthesis index, and latency modulation factor, while also considering the temporal granularity to ensure frequently accessed items are retained.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (metadata['predictive_buffer'][key] +
                 metadata['dynamic_synthesis'][key] +
                 metadata['latency_modulation'][key]) / (1 + metadata['temporal_granularity'][key])
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive buffer score is increased to reflect the likelihood of future accesses, the dynamic synthesis index is adjusted to reflect the current access pattern, the latency modulation factor is recalibrated based on the time since last access, and the temporal granularity counter is incremented.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['predictive_buffer'][key] += 1
    metadata['dynamic_synthesis'][key] *= 1.1  # Example adjustment
    time_since_last_access = cache_snapshot.access_count - metadata['last_access_time'][key]
    metadata['latency_modulation'][key] = 1 / (1 + time_since_last_access)
    metadata['temporal_granularity'][key] += 1
    metadata['last_access_time'][key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the predictive buffer score is initialized based on historical data, the dynamic synthesis index is set to a neutral value, the latency modulation factor is calculated based on expected access urgency, and the temporal granularity counter is initialized to zero.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['predictive_buffer'][key] = PREDICTIVE_BUFFER_INIT
    metadata['dynamic_synthesis'][key] = DYNAMIC_SYNTHESIS_NEUTRAL
    metadata['latency_modulation'][key] = LATENCY_MODULATION_INIT
    metadata['temporal_granularity'][key] = TEMPORAL_GRANULARITY_INIT
    metadata['last_access_time'][key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the predictive buffer scores of remaining entries are recalibrated to reflect the new cache state, the dynamic synthesis index is adjusted to account for the change in access patterns, the latency modulation factor is updated to reflect the reduced cache size, and the temporal granularity counters are normalized.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        metadata['predictive_buffer'][key] *= 0.9  # Example recalibration
        metadata['dynamic_synthesis'][key] *= 0.95  # Example adjustment
        metadata['latency_modulation'][key] *= 1.05  # Example update
        metadata['temporal_granularity'][key] = max(0, metadata['temporal_granularity'][key] - 1)