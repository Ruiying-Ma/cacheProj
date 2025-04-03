# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
TEMPORAL_WEIGHT = 0.7
SPATIAL_WEIGHT = 0.3

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive score for each cache entry based on historical access patterns, spatial locality metrics, and temporal access trends. It also tracks a resource equilibrium index to balance cache resources across different data types or access patterns.
predictive_scores = defaultdict(lambda: 0)
resource_equilibrium_index = defaultdict(lambda: 1)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest predictive score, which is calculated using a fusion of spatio-temporal analysis and algorithmic predictions. The resource equilibrium index is also considered to ensure balanced resource allocation.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        score = predictive_scores[key] * resource_equilibrium_index[key]
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive score of the accessed entry is recalibrated using recent access data, enhancing its temporal weight. The spatial locality metrics are updated to reflect the current access pattern, and the resource equilibrium index is adjusted to account for the hit.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    predictive_scores[obj.key] = (predictive_scores[obj.key] * TEMPORAL_WEIGHT) + (cache_snapshot.access_count * (1 - TEMPORAL_WEIGHT))
    resource_equilibrium_index[obj.key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its predictive score using initial spatio-temporal data and sets a baseline for its resource equilibrium index. The overall cache metadata is adjusted to incorporate the new entry's impact on spatial and temporal dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    predictive_scores[obj.key] = cache_snapshot.access_count * SPATIAL_WEIGHT
    resource_equilibrium_index[obj.key] = 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the predictive scores of remaining entries to reflect the changed cache state. The spatial locality metrics are updated to remove the evicted entry's influence, and the resource equilibrium index is adjusted to maintain balance across the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    del predictive_scores[evicted_obj.key]
    del resource_equilibrium_index[evicted_obj.key]
    for key in cache_snapshot.cache:
        predictive_scores[key] *= 0.9  # Decay factor to adjust scores