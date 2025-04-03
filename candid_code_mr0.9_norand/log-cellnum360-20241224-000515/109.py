# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_PRIORITY_THRESHOLD = 1
LOAD_BALANCE_FACTOR = 1.0
DYNAMIC_BUFFER_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a Priority Threshold for each cache entry, a Load Balancing score to distribute cache load evenly, Temporal Mapping to track access patterns over time, and a Dynamic Buffer to adjust cache space allocation dynamically.
priority_threshold = defaultdict(lambda: INITIAL_PRIORITY_THRESHOLD)
load_balancing_score = defaultdict(float)
temporal_mapping = {}
dynamic_buffer = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first identifying entries below the Priority Threshold, then selecting the entry with the lowest Load Balancing score, and finally considering the least recently accessed entry based on Temporal Mapping.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    # Step 1: Identify entries below the Priority Threshold
    candidates = [key for key, cached_obj in cache_snapshot.cache.items() 
                  if priority_threshold[key] < priority_threshold[obj.key]]

    # Step 2: Select the entry with the lowest Load Balancing score
    if candidates:
        candid_obj_key = min(candidates, key=lambda k: (load_balancing_score[k], temporal_mapping[k]))
    else:
        # If no candidates, fall back to least recently accessed
        candid_obj_key = min(cache_snapshot.cache.keys(), key=lambda k: temporal_mapping[k])
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Priority Threshold for the accessed entry is increased, the Load Balancing score is adjusted to reflect the current load distribution, and the Temporal Mapping is updated to mark the recent access time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    priority_threshold[obj.key] += 1
    load_balancing_score[obj.key] = (load_balancing_score[obj.key] + LOAD_BALANCE_FACTOR) / 2
    temporal_mapping[obj.key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Priority Threshold is initialized based on initial access frequency predictions, the Load Balancing score is recalculated to include the new entry, and the Temporal Mapping is set to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    priority_threshold[obj.key] = INITIAL_PRIORITY_THRESHOLD
    load_balancing_score[obj.key] = LOAD_BALANCE_FACTOR
    temporal_mapping[obj.key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the Dynamic Buffer is adjusted to potentially increase space for higher priority entries, the Load Balancing scores are recalibrated to reflect the new cache state, and the Temporal Mapping is updated to remove the evicted entry's history.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    # Adjust Dynamic Buffer
    dynamic_buffer = int(cache_snapshot.capacity * DYNAMIC_BUFFER_FACTOR)
    
    # Recalibrate Load Balancing scores
    for key in cache_snapshot.cache:
        load_balancing_score[key] = (load_balancing_score[key] + LOAD_BALANCE_FACTOR) / 2
    
    # Remove evicted entry's history
    if evicted_obj.key in priority_threshold:
        del priority_threshold[evicted_obj.key]
    if evicted_obj.key in load_balancing_score:
        del load_balancing_score[evicted_obj.key]
    if evicted_obj.key in temporal_mapping:
        del temporal_mapping[evicted_obj.key]