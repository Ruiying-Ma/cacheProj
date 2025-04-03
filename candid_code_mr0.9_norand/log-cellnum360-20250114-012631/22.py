# Import anything you need below
import time

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for access frequency
BETA = 0.3   # Weight for recency
GAMMA = 0.1  # Weight for contextual importance
DELTA = 0.1  # Weight for bias adjustment

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency of access, contextual importance score, and a bias adjustment factor for each cached object.
metadata = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a weighted score for each object, combining access frequency, recency, contextual importance, and bias adjustment. The object with the lowest score is evicted.
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
        score = (ALPHA * meta['access_frequency'] +
                 BETA * (cache_snapshot.access_count - meta['recency']) +
                 GAMMA * meta['contextual_importance'] +
                 DELTA * meta['bias_adjustment'])
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy increases the access frequency, updates the recency timestamp, recalculates the contextual importance score based on real-time analytics, and adjusts the bias factor to refine predictive modeling.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    meta = metadata[key]
    meta['access_frequency'] += 1
    meta['recency'] = cache_snapshot.access_count
    meta['contextual_importance'] = calculate_contextual_importance(obj)
    meta['bias_adjustment'] = adjust_bias_factor(meta)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the recency timestamp to the current time, assigns an initial contextual importance score based on the insertion context, and sets a neutral bias adjustment factor.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata[key] = {
        'access_frequency': 1,
        'recency': cache_snapshot.access_count,
        'contextual_importance': calculate_contextual_importance(obj),
        'bias_adjustment': 0.0
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy recalculates the bias adjustment factor to account for the eviction's impact on predictive modeling, and updates the contextual importance scores of remaining objects to reflect the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del metadata[evicted_key]
    
    for key, meta in metadata.items():
        meta['bias_adjustment'] = adjust_bias_factor(meta)
        meta['contextual_importance'] = calculate_contextual_importance(cache_snapshot.cache[key])

def calculate_contextual_importance(obj):
    # Placeholder for real-time analytics to calculate contextual importance
    return 1.0

def adjust_bias_factor(meta):
    # Placeholder for adjusting bias factor based on predictive modeling
    return 0.0