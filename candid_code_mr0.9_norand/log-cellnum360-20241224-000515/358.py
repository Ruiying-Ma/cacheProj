# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
DYNAMIC_PRIORITY_WEIGHT = 0.4
CONTEXT_AWARE_WEIGHT = 0.3
PREDICTIVE_EFFICIENCY_WEIGHT = 0.2
LOAD_BALANCING_WEIGHT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a dynamic priority score for each cache entry, a context-aware score based on access patterns, a predictive efficiency model score estimating future access likelihood, and a load balancing indicator reflecting system load.
dynamic_priority_scores = defaultdict(float)
context_aware_scores = defaultdict(float)
predictive_efficiency_scores = defaultdict(float)
load_balancing_indicator = 1.0  # Assume a normalized load balancing indicator

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest combined score from the dynamic priority, context-aware, and predictive efficiency model, while considering the load balancing indicator to avoid overloading any part of the system.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (
            DYNAMIC_PRIORITY_WEIGHT * dynamic_priority_scores[key] +
            CONTEXT_AWARE_WEIGHT * context_aware_scores[key] +
            PREDICTIVE_EFFICIENCY_WEIGHT * predictive_efficiency_scores[key] +
            LOAD_BALANCING_WEIGHT * load_balancing_indicator
        )
        
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the dynamic priority score is increased, the context-aware score is adjusted based on recent access patterns, and the predictive efficiency model is updated to reflect the increased likelihood of future accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    dynamic_priority_scores[obj.key] += 1.0
    context_aware_scores[obj.key] += 0.5  # Example adjustment
    predictive_efficiency_scores[obj.key] += 0.3  # Example adjustment

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the dynamic priority score is initialized, the context-aware score is set based on initial access context, and the predictive efficiency model is updated to include the new entry's potential future access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    dynamic_priority_scores[obj.key] = 1.0
    context_aware_scores[obj.key] = 0.5  # Initial context score
    predictive_efficiency_scores[obj.key] = 0.3  # Initial predictive score

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the load balancing indicator is adjusted to reflect the change in cache load, and the predictive efficiency model is recalibrated to account for the removal of the evicted entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Adjust load balancing indicator
    load_balancing_indicator = cache_snapshot.size / cache_snapshot.capacity
    
    # Recalibrate predictive efficiency model
    if evicted_obj.key in predictive_efficiency_scores:
        del predictive_efficiency_scores[evicted_obj.key]