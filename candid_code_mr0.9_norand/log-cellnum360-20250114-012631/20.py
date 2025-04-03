# Import anything you need below
import time

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for recency in dynamic priority score
BETA = 0.3   # Weight for access frequency in dynamic priority score
GAMMA = 0.2  # Weight for predicted next access time in dynamic priority score

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, predicted next access time, and a dynamic priority score for each cache entry.
metadata = {}

def calculate_priority_score(freq, last_access, predicted_next_access, current_time):
    recency = current_time - last_access
    return ALPHA * recency + BETA * freq + GAMMA * predicted_next_access

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on the lowest dynamic priority score, which is calculated using a combination of access frequency, recency, and predicted next access time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    lowest_priority_score = float('inf')
    current_time = cache_snapshot.access_count

    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        priority_score = calculate_priority_score(meta['freq'], meta['last_access'], meta['predicted_next_access'], current_time)
        if priority_score < lowest_priority_score:
            lowest_priority_score = priority_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency is incremented, the last access timestamp is updated to the current time, and the predicted next access time is adjusted based on observed access patterns. The dynamic priority score is recalculated.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    meta = metadata[obj.key]
    meta['freq'] += 1
    meta['last_access'] = current_time
    meta['predicted_next_access'] = current_time + (current_time - meta['last_access']) / meta['freq']
    meta['priority_score'] = calculate_priority_score(meta['freq'], meta['last_access'], meta['predicted_next_access'], current_time)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the initial access frequency is set to 1, the last access timestamp is set to the current time, the predicted next access time is estimated based on similar objects, and the dynamic priority score is initialized.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    metadata[obj.key] = {
        'freq': 1,
        'last_access': current_time,
        'predicted_next_access': current_time + 1,  # Initial prediction
        'priority_score': calculate_priority_score(1, current_time, current_time + 1, current_time)
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy re-evaluates the dynamic priority scores of remaining entries to ensure they reflect the most current access patterns and predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    del metadata[evicted_obj.key]
    for key, meta in metadata.items():
        meta['priority_score'] = calculate_priority_score(meta['freq'], meta['last_access'], meta['predicted_next_access'], current_time)