# Import anything you need below
import time

# Put tunable constant parameters below
PREDICTIVE_SCORE_INCREMENT = 1
DELAYED_EVICTION_THRESHOLD = 10
TIME_THRESHOLD = 5

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive score for each cache entry, a timestamp of the last access, and a delayed eviction flag. The predictive score is based on historical access patterns and temporal locality, while the delayed eviction flag indicates if an entry is temporarily protected from eviction.
cache_metadata = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest predictive score that does not have the delayed eviction flag set. If all entries have the flag set, the policy waits until the flag is cleared based on a time threshold.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    current_time = cache_snapshot.access_count

    for key, cached_obj in cache_snapshot.cache.items():
        metadata = cache_metadata[key]
        if not metadata['delayed_eviction'] or (current_time - metadata['last_access'] > TIME_THRESHOLD):
            if metadata['predictive_score'] < min_score:
                min_score = metadata['predictive_score']
                candid_obj_key = key

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the predictive score by increasing it slightly to reflect the temporal locality, updates the last access timestamp to the current time, and may set the delayed eviction flag if the score surpasses a certain threshold.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    metadata = cache_metadata[obj.key]
    metadata['predictive_score'] += PREDICTIVE_SCORE_INCREMENT
    metadata['last_access'] = cache_snapshot.access_count

    if metadata['predictive_score'] > DELAYED_EVICTION_THRESHOLD:
        metadata['delayed_eviction'] = True

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its predictive score based on initial access patterns, sets the last access timestamp to the current time, and leaves the delayed eviction flag unset initially.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    cache_metadata[obj.key] = {
        'predictive_score': 0,
        'last_access': cache_snapshot.access_count,
        'delayed_eviction': False
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalibrates the predictive scores of remaining entries to ensure they reflect the most recent access patterns, clears the delayed eviction flag for all entries, and updates any global statistics used for prediction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    if evicted_obj.key in cache_metadata:
        del cache_metadata[evicted_obj.key]

    for key, metadata in cache_metadata.items():
        metadata['predictive_score'] = max(0, metadata['predictive_score'] - 1)
        metadata['delayed_eviction'] = False