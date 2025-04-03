# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
SYNC_WEIGHT = 1.0
LOAD_WEIGHT = 1.0
PRIORITY_WEIGHT = 1.0
LATENCY_WEIGHT = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry, including a synchronization score, load balance weight, priority level, and access latency. The synchronization score reflects the frequency and recency of data synchronization needs. The load balance weight indicates the current load distribution across cache entries. The priority level is assigned based on the importance of the data. Access latency records the time taken for recent accesses.
metadata = defaultdict(lambda: {
    'sync_score': 0,
    'load_weight': 0,
    'priority_level': 0,
    'access_latency': 0
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each entry, which is a weighted sum of the synchronization score, load balance weight, priority level, and access latency. The entry with the lowest composite score is selected for eviction, ensuring that less critical, less synchronized, and higher latency entries are removed first.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        composite_score = (
            SYNC_WEIGHT * meta['sync_score'] +
            LOAD_WEIGHT * meta['load_weight'] +
            PRIORITY_WEIGHT * meta['priority_level'] +
            LATENCY_WEIGHT * meta['access_latency']
        )
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the synchronization score is incremented to reflect increased synchronization needs, the load balance weight is adjusted to reflect the current load, the priority level is re-evaluated based on recent access patterns, and the access latency is updated to reflect the latest access time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['sync_score'] += 1
    meta['load_weight'] = len(cache_snapshot.cache) / cache_snapshot.capacity
    meta['priority_level'] += 1
    meta['access_latency'] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the synchronization score is initialized based on expected synchronization needs, the load balance weight is set to distribute load evenly, the priority level is assigned based on initial importance, and the access latency is recorded as the time of insertion.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['sync_score'] = 1
    meta['load_weight'] = len(cache_snapshot.cache) / cache_snapshot.capacity
    meta['priority_level'] = 1
    meta['access_latency'] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalibrates the load balance weights of remaining entries to ensure even distribution, adjusts synchronization scores to reflect the reduced cache size, and re-evaluates priority levels to maintain optimal cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        meta = metadata[key]
        meta['load_weight'] = len(cache_snapshot.cache) / cache_snapshot.capacity
        meta['sync_score'] = max(0, meta['sync_score'] - 1)
        meta['priority_level'] = max(0, meta['priority_level'] - 1)