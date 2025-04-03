# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
QUANTUM_EVICTION_THRESHOLD = 5  # Example threshold for quantum eviction

# Put the metadata specifically maintained by the policy below. The policy maintains a temporal consistency score for each cache entry, a load prediction metric for the system, a quantum eviction counter, and a hierarchical score that combines recency, frequency, and importance of access.
temporal_consistency_scores = defaultdict(int)
hierarchical_scores = defaultdict(int)
quantum_eviction_counter = 0
load_prediction_metric = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first checking the quantum eviction counter; if it reaches a threshold, the entry with the lowest hierarchical score is evicted. If the counter is not triggered, the entry with the lowest temporal consistency score is considered for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    if quantum_eviction_counter >= QUANTUM_EVICTION_THRESHOLD:
        # Evict based on hierarchical score
        candid_obj_key = min(cache_snapshot.cache.keys(), key=lambda k: hierarchical_scores[k])
    else:
        # Evict based on temporal consistency score
        candid_obj_key = min(cache_snapshot.cache.keys(), key=lambda k: temporal_consistency_scores[k])
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the temporal consistency score of the accessed entry is increased, the hierarchical score is recalculated to reflect the recent access, and the load prediction metric is adjusted based on current system load trends.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    temporal_consistency_scores[obj.key] += 1
    hierarchical_scores[obj.key] = temporal_consistency_scores[obj.key] + cache_snapshot.access_count
    load_prediction_metric = cache_snapshot.size / cache_snapshot.capacity

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the temporal consistency score is initialized, the hierarchical score is set based on initial access patterns, and the quantum eviction counter is incremented to track the number of insertions since the last eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    temporal_consistency_scores[obj.key] = 1
    hierarchical_scores[obj.key] = cache_snapshot.access_count
    global quantum_eviction_counter
    quantum_eviction_counter += 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the quantum eviction counter is reset, the load prediction metric is updated to reflect the reduced cache load, and the hierarchical scores of remaining entries are adjusted to account for the change in cache composition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    global quantum_eviction_counter
    quantum_eviction_counter = 0
    load_prediction_metric = cache_snapshot.size / cache_snapshot.capacity
    for key in cache_snapshot.cache:
        hierarchical_scores[key] = temporal_consistency_scores[key] + cache_snapshot.access_count