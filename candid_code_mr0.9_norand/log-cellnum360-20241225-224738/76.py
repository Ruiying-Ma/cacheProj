# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
PATTERN_SCORE_DECAY = 0.9  # Decay factor for pattern score adjustment

# Put the metadata specifically maintained by the policy below. The policy maintains a frequency count for each cache entry, a timestamp of the last access, and a pattern score derived from recent access patterns. It also keeps a global synchronization counter to manage concurrent access.
frequency_count = defaultdict(int)
last_access_time = {}
pattern_score = defaultdict(float)
global_sync_counter = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest pattern score, breaking ties by choosing the entry with the lowest frequency count, and further ties by selecting the oldest entry based on the timestamp.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_pattern_score = float('inf')
    min_frequency = float('inf')
    oldest_time = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        if (pattern_score[key] < min_pattern_score or
            (pattern_score[key] == min_pattern_score and frequency_count[key] < min_frequency) or
            (pattern_score[key] == min_pattern_score and frequency_count[key] == min_frequency and last_access_time[key] < oldest_time)):
            min_pattern_score = pattern_score[key]
            min_frequency = frequency_count[key]
            oldest_time = last_access_time[key]
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the frequency count of the accessed entry is incremented, the timestamp is updated to the current time, and the pattern score is recalculated based on recent access patterns. The global synchronization counter is incremented to ensure consistency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    global global_sync_counter
    key = obj.key
    frequency_count[key] += 1
    last_access_time[key] = cache_snapshot.access_count
    pattern_score[key] = frequency_count[key] / (cache_snapshot.access_count - last_access_time[key] + 1)
    global_sync_counter += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the frequency count is initialized to one, the timestamp is set to the current time, and the pattern score is calculated based on initial access predictions. The global synchronization counter is incremented to maintain order.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    global global_sync_counter
    key = obj.key
    frequency_count[key] = 1
    last_access_time[key] = cache_snapshot.access_count
    pattern_score[key] = 1.0  # Initial pattern score
    global_sync_counter += 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the global synchronization counter is decremented to reflect the removal of an entry, and the pattern scores of remaining entries are adjusted to account for the change in cache dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    global global_sync_counter
    evicted_key = evicted_obj.key
    del frequency_count[evicted_key]
    del last_access_time[evicted_key]
    del pattern_score[evicted_key]
    
    global_sync_counter -= 1
    
    # Adjust pattern scores for remaining entries
    for key in cache_snapshot.cache:
        pattern_score[key] *= PATTERN_SCORE_DECAY