# Import anything you need below
from collections import defaultdict
import time

# Put tunable constant parameters below
INITIAL_PRIORITY_SCORE = 1
PRIORITY_INCREMENT = 1
BUFFER_ADJUSTMENT_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a priority score for each cache entry, an adaptive buffer size for each priority level, and a real-time update timestamp for each entry. It also keeps a checkpoint log to track changes in priority scores and buffer sizes over time.
priority_scores = defaultdict(lambda: INITIAL_PRIORITY_SCORE)
update_timestamps = {}
buffer_sizes = defaultdict(lambda: 0)
checkpoint_log = []

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest priority score within the least recently updated buffer. If multiple entries have the same score, it uses the oldest checkpoint log entry to break ties.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_priority = float('inf')
    oldest_timestamp = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        priority = priority_scores[key]
        timestamp = update_timestamps.get(key, 0)
        
        if priority < min_priority or (priority == min_priority and timestamp < oldest_timestamp):
            min_priority = priority
            oldest_timestamp = timestamp
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the priority score of the accessed entry and updates its real-time timestamp. It also adjusts the adaptive buffer size based on recent access patterns and logs this change in the checkpoint.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    priority_scores[obj.key] += PRIORITY_INCREMENT
    update_timestamps[obj.key] = cache_snapshot.access_count
    
    # Adjust buffer size
    buffer_sizes[obj.key] += BUFFER_ADJUSTMENT_FACTOR
    checkpoint_log.append((cache_snapshot.access_count, obj.key, 'hit', priority_scores[obj.key], buffer_sizes[obj.key]))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial priority score based on the object's predicted access frequency and updates the real-time timestamp. It recalibrates the adaptive buffer sizes to accommodate the new entry and logs these changes in the checkpoint.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    priority_scores[obj.key] = INITIAL_PRIORITY_SCORE
    update_timestamps[obj.key] = cache_snapshot.access_count
    
    # Recalibrate buffer sizes
    buffer_sizes[obj.key] = obj.size
    checkpoint_log.append((cache_snapshot.access_count, obj.key, 'insert', priority_scores[obj.key], buffer_sizes[obj.key]))

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy decreases the buffer size of the evicted entry's priority level if necessary and updates the checkpoint log to reflect the eviction. It also recalculates priority scores for remaining entries to ensure optimal cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in buffer_sizes:
        del buffer_sizes[evicted_obj.key]
    
    checkpoint_log.append((cache_snapshot.access_count, evicted_obj.key, 'evict', priority_scores[evicted_obj.key], buffer_sizes.get(evicted_obj.key, 0)))
    
    # Recalculate priority scores for remaining entries
    for key in cache_snapshot.cache:
        priority_scores[key] = max(INITIAL_PRIORITY_SCORE, priority_scores[key] - PRIORITY_INCREMENT)