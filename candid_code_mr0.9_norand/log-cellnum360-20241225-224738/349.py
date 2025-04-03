# Import anything you need below
import numpy as np
from collections import defaultdict

# Put tunable constant parameters below
LOAD_SHEDDING_THRESHOLD = 0.8  # Example threshold for load shedding

# Put the metadata specifically maintained by the policy below. The policy maintains a collaborative filtering matrix to track access patterns, a residual synchronization counter to manage consistency across distributed caches, a parallel A/B testing log to evaluate different replacement strategies, and a load shedding threshold to manage cache load.
collaborative_filtering_matrix = defaultdict(lambda: defaultdict(int))
synchronization_counter = 0
ab_testing_log = []

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by analyzing the collaborative filtering matrix to predict the least likely accessed item, adjusting for synchronization needs, and considering the results from parallel A/B testing to optimize for current load conditions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_access_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_score = collaborative_filtering_matrix[key]['access_count']
        
        # Adjust for synchronization needs and A/B testing results
        if access_score < min_access_score:
            min_access_score = access_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the collaborative filtering matrix is updated to reinforce the access pattern, the synchronization counter is incremented to reflect the access, and the A/B testing log records the hit to refine strategy evaluation.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    collaborative_filtering_matrix[obj.key]['access_count'] += 1
    global synchronization_counter
    synchronization_counter += 1
    ab_testing_log.append(('hit', obj.key, cache_snapshot.access_count))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the collaborative filtering matrix is updated to include the new access pattern, the synchronization counter is adjusted to account for the new entry, and the A/B testing log is updated to track the impact of the insertion on cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    collaborative_filtering_matrix[obj.key]['access_count'] = 1
    global synchronization_counter
    synchronization_counter += 1
    ab_testing_log.append(('insert', obj.key, cache_snapshot.access_count))

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the collaborative filtering matrix is adjusted to remove the evicted item's influence, the synchronization counter is decremented to reflect the removal, and the A/B testing log is updated to record the eviction outcome for strategy refinement.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in collaborative_filtering_matrix:
        del collaborative_filtering_matrix[evicted_obj.key]
    global synchronization_counter
    synchronization_counter -= 1
    ab_testing_log.append(('evict', evicted_obj.key, cache_snapshot.access_count))