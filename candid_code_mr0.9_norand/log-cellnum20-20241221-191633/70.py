# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
DEFAULT_ACCESS_FREQUENCY = 1
DEFAULT_RECENCY = 0
PRIORITY_WEIGHT_FREQUENCY = 0.5
PRIORITY_WEIGHT_RECENCY = 0.3
PRIORITY_WEIGHT_GLOBAL = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains a profile for each cache entry, including access frequency, recency of access, and a dynamic priority score. It also tracks a global adjustment factor that periodically influences the priority scores based on overall cache performance metrics.
cache_metadata = defaultdict(lambda: {
    'access_frequency': DEFAULT_ACCESS_FREQUENCY,
    'recency': DEFAULT_RECENCY,
    'priority_score': 0
})
global_adjustment_factor = 1.0

def calculate_priority_score(access_frequency, recency, global_adjustment_factor):
    return (PRIORITY_WEIGHT_FREQUENCY * access_frequency +
            PRIORITY_WEIGHT_RECENCY * recency +
            PRIORITY_WEIGHT_GLOBAL * global_adjustment_factor)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest priority score, which is a combination of its access frequency, recency, and the global adjustment factor. This ensures that less frequently accessed and older entries are more likely to be evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_priority_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        priority_score = cache_metadata[key]['priority_score']
        if priority_score < min_priority_score:
            min_priority_score = priority_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency and recency of the accessed entry are updated. The priority score is recalculated to reflect the increased likelihood of future access, taking into account the global adjustment factor.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    metadata = cache_metadata[obj.key]
    metadata['access_frequency'] += 1
    metadata['recency'] = cache_snapshot.access_count
    metadata['priority_score'] = calculate_priority_score(
        metadata['access_frequency'],
        metadata['recency'],
        global_adjustment_factor
    )

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency and recency to default values. The priority score is set based on these initial values and the current global adjustment factor, ensuring new entries are fairly considered in future evictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    cache_metadata[obj.key] = {
        'access_frequency': DEFAULT_ACCESS_FREQUENCY,
        'recency': cache_snapshot.access_count,
        'priority_score': calculate_priority_score(
            DEFAULT_ACCESS_FREQUENCY,
            cache_snapshot.access_count,
            global_adjustment_factor
        )
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the global adjustment factor is recalibrated based on recent cache performance, such as hit rate and eviction frequency. This recalibration influences the priority scores of remaining entries, optimizing the cache for current access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    global global_adjustment_factor
    hit_rate = cache_snapshot.hit_count / max(1, cache_snapshot.access_count)
    global_adjustment_factor = 1 + (hit_rate - 0.5)  # Adjust based on hit rate

    # Recalculate priority scores for all remaining entries
    for key, cached_obj in cache_snapshot.cache.items():
        metadata = cache_metadata[key]
        metadata['priority_score'] = calculate_priority_score(
            metadata['access_frequency'],
            metadata['recency'],
            global_adjustment_factor
        )