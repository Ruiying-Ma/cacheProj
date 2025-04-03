# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
DEFAULT_RECOVERY_PRIORITY_SCORE = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a transaction log for each cache entry, a consistency validation timestamp, a recovery priority score, and a data persistence flag indicating if the data is critical for system recovery.
transaction_logs = defaultdict(list)
consistency_validation_timestamps = {}
recovery_priority_scores = {}
data_persistence_flags = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a combination of the lowest recovery priority score and the oldest consistency validation timestamp, ensuring that non-critical and less recently validated data is evicted first.
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
        if (recovery_priority_scores[key] < min_priority or
            (recovery_priority_scores[key] == min_priority and 
             consistency_validation_timestamps[key] < oldest_timestamp)):
            if not data_persistence_flags[key]:  # Prefer non-critical data
                min_priority = recovery_priority_scores[key]
                oldest_timestamp = consistency_validation_timestamps[key]
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the consistency validation timestamp to the current time and increments the recovery priority score, indicating increased importance for system recovery.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    consistency_validation_timestamps[obj.key] = cache_snapshot.access_count
    recovery_priority_scores[obj.key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the transaction log, sets the consistency validation timestamp to the current time, assigns a default recovery priority score, and sets the data persistence flag based on the object's criticality.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    transaction_logs[obj.key] = []
    consistency_validation_timestamps[obj.key] = cache_snapshot.access_count
    recovery_priority_scores[obj.key] = DEFAULT_RECOVERY_PRIORITY_SCORE
    data_persistence_flags[obj.key] = False  # Assume non-critical by default

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the policy archives the transaction log for potential system recovery analysis and adjusts the recovery priority scores of remaining entries to reflect the change in cache composition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    # Archive the transaction log
    archived_log = transaction_logs.pop(evicted_obj.key, None)
    # Adjust recovery priority scores
    for key in cache_snapshot.cache:
        recovery_priority_scores[key] = max(1, recovery_priority_scores[key] - 1)