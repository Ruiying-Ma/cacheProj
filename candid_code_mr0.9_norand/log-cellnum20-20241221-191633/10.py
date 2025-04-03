# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
DEFAULT_PRIORITY_SCORE = 1
PRIORITY_DECREASE_FACTOR = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains a priority score for each cache entry, a timestamp of last access, and a retention counter that tracks how many times an entry has been retained during eviction attempts.
priority_scores = defaultdict(lambda: DEFAULT_PRIORITY_SCORE)
last_access_timestamps = {}
retention_counters = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest priority score. If there is a tie, it selects the entry with the oldest timestamp. If still tied, it chooses the entry with the lowest retention counter.
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
    min_retention = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        priority = priority_scores[key]
        timestamp = last_access_timestamps.get(key, 0)
        retention = retention_counters[key]

        if (priority < min_priority or
            (priority == min_priority and timestamp < oldest_timestamp) or
            (priority == min_priority and timestamp == oldest_timestamp and retention < min_retention)):
            min_priority = priority
            oldest_timestamp = timestamp
            min_retention = retention
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the priority score of the accessed entry is increased, the timestamp is updated to the current time, and the retention counter is reset to zero.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    priority_scores[key] += 1
    last_access_timestamps[key] = cache_snapshot.access_count
    retention_counters[key] = 0

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns it a default priority score, sets the current timestamp, and initializes the retention counter to zero.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    priority_scores[key] = DEFAULT_PRIORITY_SCORE
    last_access_timestamps[key] = cache_snapshot.access_count
    retention_counters[key] = 0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy decreases the priority scores of all remaining entries slightly to allow for dynamic priority adjustment over time, and increments the retention counter of the evicted entry if it was retained in previous eviction attempts.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if retention_counters[evicted_key] > 0:
        retention_counters[evicted_key] += 1

    for key in cache_snapshot.cache:
        priority_scores[key] *= PRIORITY_DECREASE_FACTOR