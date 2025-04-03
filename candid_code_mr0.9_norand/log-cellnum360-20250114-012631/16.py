# Import anything you need below
import math

# Put tunable constant parameters below
ENTROPY_WEIGHT = 0.5
FREQUENCY_WEIGHT = 0.3
RESIDENCY_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry including access frequency, last access timestamp, insertion timestamp, and an entropy score calculated based on access patterns.
metadata = {}

def calculate_entropy(access_times):
    if len(access_times) < 2:
        return 0
    intervals = [access_times[i] - access_times[i-1] for i in range(1, len(access_times))]
    mean_interval = sum(intervals) / len(intervals)
    entropy = -sum((interval / mean_interval) * math.log(interval / mean_interval) for interval in intervals) / len(intervals)
    return entropy

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by balancing between the least frequently accessed entries, the longest residency time, and the highest entropy score to ensure a mix of old and less useful data is evicted.
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
        meta = metadata[key]
        frequency = meta['frequency']
        last_access = meta['last_access']
        insertion_time = meta['insertion_time']
        entropy = meta['entropy']

        residency_time = current_time - insertion_time
        score = (ENTROPY_WEIGHT * entropy) + (FREQUENCY_WEIGHT * frequency) + (RESIDENCY_WEIGHT * residency_time)

        if score < min_score:
            min_score = score
            candid_obj_key = key

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency is incremented, the last access timestamp is updated to the current time, and the entropy score is recalculated based on the updated access history.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    key = obj.key
    meta = metadata[key]
    meta['frequency'] += 1
    meta['last_access'] = current_time
    meta['access_times'].append(current_time)
    meta['entropy'] = calculate_entropy(meta['access_times'])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the insertion timestamp is set to the current time, access frequency is initialized to 1, the last access timestamp is set to the current time, and the entropy score is initialized based on initial access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    key = obj.key
    metadata[key] = {
        'frequency': 1,
        'last_access': current_time,
        'insertion_time': current_time,
        'access_times': [current_time],
        'entropy': 0
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalculates the entropy scores for the remaining entries to ensure balanced entropy distribution and updates any global statistics used for eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata:
        del metadata[evicted_key]

    for key, meta in metadata.items():
        meta['entropy'] = calculate_entropy(meta['access_times'])