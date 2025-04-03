# Import anything you need below
from collections import defaultdict
import time

# Put tunable constant parameters below
INITIAL_PRIORITY = 1.0
CRITICAL_BUFFER_THRESHOLD = 0.5
LOAD_VARIANCE_DECAY = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains a priority score for each cache entry, a timestamp of the last access, a buffer optimization flag indicating if the entry is part of a critical buffer, and a load variance metric that tracks the frequency of access changes over time.
priority_scores = defaultdict(lambda: INITIAL_PRIORITY)
timestamps = {}
buffer_flags = defaultdict(bool)
load_variance = 0.0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first considering entries with the lowest priority scores. Among these, it selects the entry with the oldest timestamp, unless the entry is part of a critical buffer, in which case it recalibrates priorities to protect buffer integrity.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_priority = float('inf')
    oldest_time = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        if priority_scores[key] < min_priority:
            min_priority = priority_scores[key]
            oldest_time = timestamps[key]
            candid_obj_key = key
        elif priority_scores[key] == min_priority:
            if timestamps[key] < oldest_time and not buffer_flags[key]:
                oldest_time = timestamps[key]
                candid_obj_key = key
    
    # Recalibrate priorities if the chosen candidate is part of a critical buffer
    if buffer_flags[candid_obj_key]:
        for key in cache_snapshot.cache:
            priority_scores[key] *= 1.1  # Increase priority to protect buffer integrity
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy recalibrates the priority score based on the current load variance, updates the timestamp to the current time, and adjusts the buffer optimization flag if the entry's access pattern suggests a change in its criticality.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    priority_scores[key] += load_variance
    timestamps[key] = cache_snapshot.access_count
    
    # Adjust buffer flag based on access pattern
    if priority_scores[key] > CRITICAL_BUFFER_THRESHOLD:
        buffer_flags[key] = True
    else:
        buffer_flags[key] = False

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial priority score based on the current load variance, sets the timestamp to the current time, and evaluates the buffer optimization flag to determine if the entry should be part of a critical buffer.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    priority_scores[key] = INITIAL_PRIORITY + load_variance
    timestamps[key] = cache_snapshot.access_count
    
    # Evaluate buffer flag
    buffer_flags[key] = priority_scores[key] > CRITICAL_BUFFER_THRESHOLD

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the priority scores of remaining entries to reflect the new cache state, updates load variance metrics to account for the change in access patterns, and reassesses buffer optimization flags to ensure critical buffers remain intact.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    # Recalibrate priority scores
    for key in cache_snapshot.cache:
        priority_scores[key] *= LOAD_VARIANCE_DECAY
    
    # Update load variance
    load_variance = (cache_snapshot.hit_count - cache_snapshot.miss_count) / max(1, cache_snapshot.access_count)
    
    # Reassess buffer flags
    for key in cache_snapshot.cache:
        buffer_flags[key] = priority_scores[key] > CRITICAL_BUFFER_THRESHOLD