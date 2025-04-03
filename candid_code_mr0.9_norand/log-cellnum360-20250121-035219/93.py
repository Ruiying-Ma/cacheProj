# Import anything you need below
import collections

# Put tunable constant parameters below
BASE_PRIORITY = 1
INITIAL_PREDICTIVE_DEMAND = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a priority score for each cache entry, a predictive demand score based on access patterns, and a dynamic allocation factor that adjusts based on real-time usage statistics.
priority_scores = collections.defaultdict(lambda: BASE_PRIORITY)
predictive_demand_scores = collections.defaultdict(lambda: INITIAL_PREDICTIVE_DEMAND)
dynamic_allocation_factor = 1.0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache entry with the lowest combined score of priority and predictive demand, adjusted by the dynamic allocation factor to ensure balanced resource usage.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (priority_scores[key] + predictive_demand_scores[key]) * dynamic_allocation_factor
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the priority score of the accessed entry is increased, the predictive demand score is recalculated based on recent access patterns, and the dynamic allocation factor is adjusted to reflect the current usage trend.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    priority_scores[obj.key] += 1
    predictive_demand_scores[obj.key] = cache_snapshot.access_count - cache_snapshot.hit_count
    dynamic_allocation_factor = cache_snapshot.hit_count / (cache_snapshot.hit_count + cache_snapshot.miss_count)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its priority score to a base value, sets an initial predictive demand score based on historical data, and updates the dynamic allocation factor to account for the new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    priority_scores[obj.key] = BASE_PRIORITY
    predictive_demand_scores[obj.key] = INITIAL_PREDICTIVE_DEMAND
    dynamic_allocation_factor = cache_snapshot.hit_count / (cache_snapshot.hit_count + cache_snapshot.miss_count)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalculates the dynamic allocation factor to redistribute resources, adjusts the priority scores of remaining entries to reflect the new cache state, and updates predictive demand scores based on the latest access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    del priority_scores[evicted_obj.key]
    del predictive_demand_scores[evicted_obj.key]
    
    dynamic_allocation_factor = cache_snapshot.hit_count / (cache_snapshot.hit_count + cache_snapshot.miss_count)
    
    for key in cache_snapshot.cache:
        priority_scores[key] = max(BASE_PRIORITY, priority_scores[key] - 1)
        predictive_demand_scores[key] = cache_snapshot.access_count - cache_snapshot.hit_count