# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import collections

# Put tunable constant parameters below
DEFAULT_USAGE_SCORE = 1

# Put the metadata specifically maintained by the policy below. This policy maintains a matrix of access frequencies between pairs of cache entries, a timestamp of the last access for each entry, and an overall usage score for each entry.
access_frequency = collections.defaultdict(lambda: collections.defaultdict(int))
timestamps = {}
usage_scores = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first identifying entries with the lowest overall usage scores. Among those, it evicts the entry with the lowest total access frequency to other entries and the earliest timestamp.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_usage_score = min(usage_scores.values())
    candidates = [key for key, score in usage_scores.items() if score == min_usage_score]
    
    min_total_access_freq = float('inf')
    earliest_timestamp = float('inf')
    
    for key in candidates:
        total_access_freq = sum(access_frequency[key].values())
        if total_access_freq < min_total_access_freq or (total_access_freq == min_total_access_freq and timestamps[key] < earliest_timestamp):
            min_total_access_freq = total_access_freq
            earliest_timestamp = timestamps[key]
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the timestamp of the accessed entry is updated to the current time. The overall usage score of the entry is incremented. The access frequency between this entry and all others is incremented.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    current_time = cache_snapshot.access_count
    key = obj.key
    
    timestamps[key] = current_time
    usage_scores[key] += 1
    
    for other_key in cache_snapshot.cache:
        if other_key != key:
            access_frequency[key][other_key] += 1
            access_frequency[other_key][key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its timestamp is set to the current time. Its overall usage score is initialized to a default value. A new row and column for access frequencies are added to the matrix, initialized to zero.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    current_time = cache_snapshot.access_count
    key = obj.key
    
    timestamps[key] = current_time
    usage_scores[key] = DEFAULT_USAGE_SCORE
    
    for other_key in cache_snapshot.cache:
        access_frequency[key][other_key] = 0
        access_frequency[other_key][key] = 0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the metadata related to the evicted entry, including its row and column in the access frequency matrix, is removed. The overall usage scores of remaining entries are adjusted based on the removal.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    
    del timestamps[evicted_key]
    del usage_scores[evicted_key]
    
    for other_key in cache_snapshot.cache:
        if evicted_key in access_frequency[other_key]:
            del access_frequency[other_key][evicted_key]
        if evicted_key in access_frequency:
            del access_frequency[evicted_key]