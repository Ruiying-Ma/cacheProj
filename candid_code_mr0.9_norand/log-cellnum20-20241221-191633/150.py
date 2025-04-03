# Import anything you need below
from collections import defaultdict
import heapq

# Put tunable constant parameters below
PREDICTIVE_ACCESS_DECAY = 0.9  # Decay factor for predictive access pattern
INITIAL_ACCESS_PROBABILITY = 0.5  # Initial probability for new objects

# Put the metadata specifically maintained by the policy below. The policy maintains a hierarchical index of cache objects, predictive access patterns for each object, dynamic partitions of cache space based on object priority, and an event log for prioritization.
predictive_access_patterns = defaultdict(lambda: INITIAL_ACCESS_PROBABILITY)
hierarchical_index = {}
dynamic_partitions = defaultdict(int)
event_log = []

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by analyzing the predictive access patterns to identify objects with the lowest future access probability, while considering the dynamic partitioning to ensure high-priority events retain sufficient cache space.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_probability = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        access_prob = predictive_access_patterns[key]
        if access_prob < min_probability:
            min_probability = access_prob
            candid_obj_key = key
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the predictive access pattern to increase the likelihood of future access for the object and adjusts the hierarchical index to reflect the object's increased priority.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    predictive_access_patterns[obj.key] = min(1.0, predictive_access_patterns[obj.key] + (1 - PREDICTIVE_ACCESS_DECAY))
    hierarchical_index[obj.key] = cache_snapshot.access_count
    event_log.append((cache_snapshot.access_count, obj.key))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy updates the hierarchical index to include the new object, initializes its predictive access pattern, and dynamically adjusts cache partitions to accommodate the new object's priority.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    predictive_access_patterns[obj.key] = INITIAL_ACCESS_PROBABILITY
    hierarchical_index[obj.key] = cache_snapshot.access_count
    dynamic_partitions[obj.key] = obj.size
    event_log.append((cache_snapshot.access_count, obj.key))

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the object from the hierarchical index, updates the predictive access patterns of remaining objects to reflect the change, and recalibrates the dynamic partitions to optimize space for high-priority events.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in hierarchical_index:
        del hierarchical_index[evicted_obj.key]
    if evicted_obj.key in predictive_access_patterns:
        del predictive_access_patterns[evicted_obj.key]
    if evicted_obj.key in dynamic_partitions:
        del dynamic_partitions[evicted_obj.key]
    # Recalibrate dynamic partitions
    total_size = sum(dynamic_partitions.values())
    for key in dynamic_partitions:
        dynamic_partitions[key] = (dynamic_partitions[key] / total_size) * cache_snapshot.capacity
    event_log.append((cache_snapshot.access_count, evicted_obj.key))