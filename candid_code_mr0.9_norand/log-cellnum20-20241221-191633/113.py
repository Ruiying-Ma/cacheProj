# Import anything you need below
from collections import defaultdict
import heapq

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.7
RECENCY_WEIGHT = 0.3
LOAD_ADAPTABILITY_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive model for access patterns, a hierarchical index of cache objects based on access frequency and recency, and a load adaptability score that adjusts based on system load and access patterns.
access_frequency = defaultdict(int)  # Tracks how often each object is accessed
recency_index = {}  # Tracks the last access time for each object
load_adaptability_score = 1.0  # Adjusts based on system load and access patterns

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the object with the lowest combined score of predicted future access probability and current hierarchical index position, while also considering the load adaptability score to ensure real-time consistency.
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
        frequency_score = access_frequency[key]
        recency_score = cache_snapshot.access_count - recency_index[key]
        combined_score = (FREQUENCY_WEIGHT * frequency_score + 
                          RECENCY_WEIGHT * recency_score) * load_adaptability_score
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive model is updated with the new access data, the hierarchical index is adjusted to reflect the increased frequency and recency of the accessed object, and the load adaptability score is recalibrated to account for the current system load.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    access_frequency[obj.key] += 1
    recency_index[obj.key] = cache_snapshot.access_count
    load_adaptability_score = 1 + LOAD_ADAPTABILITY_FACTOR * (cache_snapshot.hit_count / (cache_snapshot.hit_count + cache_snapshot.miss_count))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the predictive model is updated to include the new object, the hierarchical index is adjusted to place the new object based on its initial access prediction, and the load adaptability score is recalibrated to reflect the change in cache composition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    access_frequency[obj.key] = 1
    recency_index[obj.key] = cache_snapshot.access_count
    load_adaptability_score = 1 + LOAD_ADAPTABILITY_FACTOR * (cache_snapshot.hit_count / (cache_snapshot.hit_count + cache_snapshot.miss_count))

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the predictive model is updated to remove the evicted object, the hierarchical index is adjusted to close the gap left by the eviction, and the load adaptability score is recalibrated to ensure the cache remains consistent with current system demands.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in access_frequency:
        del access_frequency[evicted_obj.key]
    if evicted_obj.key in recency_index:
        del recency_index[evicted_obj.key]
    load_adaptability_score = 1 + LOAD_ADAPTABILITY_FACTOR * (cache_snapshot.hit_count / (cache_snapshot.hit_count + cache_snapshot.miss_count))