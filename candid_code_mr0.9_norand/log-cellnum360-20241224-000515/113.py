# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_PRIORITY = 1.0
HIT_BOOST_FACTOR = 1.5
GLOBAL_PERFORMANCE_ADJUSTMENT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a dynamic priority score for each cache entry, which is calculated using an adaptive learning model. This model considers factors such as access frequency, recency, and a real-time evaluation of access patterns. Additionally, a global cache performance metric is tracked to adjust the learning model parameters for scalability.
priority_scores = defaultdict(lambda: INITIAL_PRIORITY)
global_cache_performance_metric = 1.0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the cache entry with the lowest dynamic priority score. This score is continuously updated based on real-time access patterns and the global cache performance metric, ensuring that the least valuable entry is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_priority = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        if priority_scores[key] < min_priority:
            min_priority = priority_scores[key]
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the priority score of the accessed entry by a factor determined by the adaptive learning model. This factor is adjusted based on the current global cache performance metric to ensure optimal performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    priority_scores[obj.key] *= HIT_BOOST_FACTOR * global_cache_performance_metric

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its priority score using the adaptive learning model, which considers the current access context and global cache performance. This ensures that new entries are appropriately prioritized from the start.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    priority_scores[obj.key] = INITIAL_PRIORITY * global_cache_performance_metric

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy updates the global cache performance metric to reflect the change in cache composition. This update influences the adaptive learning model, allowing it to recalibrate the priority scoring for remaining and future entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    del priority_scores[evicted_obj.key]
    global global_cache_performance_metric
    global_cache_performance_metric += GLOBAL_PERFORMANCE_ADJUSTMENT * (cache_snapshot.hit_count / max(1, cache_snapshot.access_count))