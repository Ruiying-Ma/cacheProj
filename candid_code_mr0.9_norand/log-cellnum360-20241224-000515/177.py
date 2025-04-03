# Import anything you need below
import math
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_PRIORITY_SCORE = 1.0
DECAY_FACTOR = 0.9
PRIORITY_BOOST = 2.0
DEFAULT_TEMPORAL_DECAY = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry including a priority score, a temporal decay factor, and a resource allocation pattern. The priority score is influenced by recent access frequency and importance of the data. The temporal decay factor reduces the priority score over time if the data is not accessed. The resource allocation pattern tracks the typical usage pattern of the data to predict future access needs.
metadata = defaultdict(lambda: {
    'priority_score': INITIAL_PRIORITY_SCORE,
    'temporal_decay': DEFAULT_TEMPORAL_DECAY,
    'last_access_time': 0
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest combined score of priority and predicted future access based on the resource allocation pattern. The temporal decay factor is applied to adjust the priority score, ensuring that stale data is more likely to be evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        # Calculate the adjusted priority score
        adjusted_priority = metadata[key]['priority_score'] * metadata[key]['temporal_decay']
        # Calculate the predicted future access score
        predicted_access = 1 / (cache_snapshot.access_count - metadata[key]['last_access_time'] + 1)
        # Combine scores
        combined_score = adjusted_priority + predicted_access
        
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the priority score of the accessed entry is boosted, and the temporal decay factor is reset to reflect the recent access. The resource allocation pattern is updated to reflect the current access time, helping to refine future predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata[key]['priority_score'] *= PRIORITY_BOOST
    metadata[key]['temporal_decay'] = DEFAULT_TEMPORAL_DECAY
    metadata[key]['last_access_time'] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the priority score based on initial access importance and sets the temporal decay factor to a default value. The resource allocation pattern is initialized to start tracking the access pattern from the point of insertion.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata[key]['priority_score'] = INITIAL_PRIORITY_SCORE
    metadata[key]['temporal_decay'] = DEFAULT_TEMPORAL_DECAY
    metadata[key]['last_access_time'] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy recalibrates the temporal decay factors of remaining entries to ensure they reflect the current cache state. The resource allocation patterns are also adjusted to account for the change in cache composition, helping to maintain accurate future access predictions.
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
        metadata[key]['temporal_decay'] *= DECAY_FACTOR