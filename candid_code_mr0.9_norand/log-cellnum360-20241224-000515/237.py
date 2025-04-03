# Import anything you need below
import math

# Put tunable constant parameters below
INITIAL_PRIORITY_WEIGHT = 1.0
SCORE_DECAY_FACTOR = 0.9
PRIORITY_ADJUSTMENT_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive score for each cache entry, which is calculated using a combination of historical access patterns, temporal dynamics, and adaptive scaling factors. It also tracks the last access time and a dynamic priority weight for each entry.
metadata = {}

def calculate_predictive_score(last_access_time, priority_weight, current_time):
    # Example calculation for predictive score
    time_since_last_access = current_time - last_access_time
    return priority_weight * math.exp(-SCORE_DECAY_FACTOR * time_since_last_access)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest predictive score, which is adjusted by its temporal dynamics and priority weight. This ensures that entries with low future access probability and low priority are evicted first.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        last_access_time = metadata[key]['last_access_time']
        priority_weight = metadata[key]['priority_weight']
        score = calculate_predictive_score(last_access_time, priority_weight, cache_snapshot.access_count)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the last access time and recalculates the predictive score by incorporating the latest access pattern. The priority weight is adjusted based on the frequency and recency of accesses to adaptively scale its importance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata[key]['last_access_time'] = cache_snapshot.access_count
    metadata[key]['priority_weight'] += PRIORITY_ADJUSTMENT_FACTOR

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its predictive score using initial access patterns and temporal dynamics. The last access time is set to the current time, and a default priority weight is assigned, which will adapt over time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata[key] = {
        'last_access_time': cache_snapshot.access_count,
        'priority_weight': INITIAL_PRIORITY_WEIGHT
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the predictive scores of remaining entries to ensure efficient optimization of cache space. It also adjusts the priority weights of similar entries to prevent frequent evictions of similar patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata:
        del metadata[evicted_key]
    
    for key in cache_snapshot.cache:
        metadata[key]['priority_weight'] *= (1 - PRIORITY_ADJUSTMENT_FACTOR)