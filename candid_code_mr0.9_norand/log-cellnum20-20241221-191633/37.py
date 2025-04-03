# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
HIGH_LOAD_THRESHOLD = 0.8  # Example threshold for high load

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, data consistency score, and load factor. The data consistency score is a measure of how often the data changes, and the load factor represents the current system load.
access_frequency = defaultdict(int)
last_access_timestamp = {}
data_consistency_score = {}
load_factor = 0.0

def calculate_data_consistency_score(obj):
    # Placeholder function to calculate data consistency score
    # This should be based on the object's change history
    return 1.0  # Example static score

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by considering the lowest data consistency score first, then the least frequently accessed item, and finally the oldest access timestamp if needed. During high load, it prioritizes evicting items with low access frequency and low consistency scores to reduce latency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    min_freq = float('inf')
    oldest_time = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        score = data_consistency_score.get(key, float('inf'))
        freq = access_frequency.get(key, 0)
        last_time = last_access_timestamp.get(key, float('inf'))

        if load_factor > HIGH_LOAD_THRESHOLD:
            # During high load, prioritize low frequency and low score
            if (freq < min_freq) or (freq == min_freq and score < min_score):
                min_freq = freq
                min_score = score
                candid_obj_key = key
        else:
            # Normal eviction policy
            if (score < min_score) or (score == min_score and freq < min_freq) or (score == min_score and freq == min_freq and last_time < oldest_time):
                min_score = score
                min_freq = freq
                oldest_time = last_time
                candid_obj_key = key

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the access frequency of the item is incremented, and the last access timestamp is updated to the current time. The data consistency score is recalculated based on recent changes to the data, if any.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    access_frequency[obj.key] += 1
    last_access_timestamp[obj.key] = cache_snapshot.access_count
    data_consistency_score[obj.key] = calculate_data_consistency_score(obj)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the access frequency is initialized to one, the last access timestamp is set to the current time, and the data consistency score is calculated based on the object's change history. The load factor is adjusted to reflect the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    access_frequency[obj.key] = 1
    last_access_timestamp[obj.key] = cache_snapshot.access_count
    data_consistency_score[obj.key] = calculate_data_consistency_score(obj)
    load_factor = cache_snapshot.size / cache_snapshot.capacity

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an item, the load factor is recalculated to reflect the reduced cache occupancy. The policy may also adjust the data consistency scores of remaining items if the evicted item was frequently updated, indicating a potential change in data patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    load_factor = cache_snapshot.size / cache_snapshot.capacity
    if access_frequency[evicted_obj.key] > 10:  # Example threshold for frequent updates
        for key in cache_snapshot.cache:
            data_consistency_score[key] = calculate_data_consistency_score(cache_snapshot.cache[key])
    # Clean up metadata for evicted object
    del access_frequency[evicted_obj.key]
    del last_access_timestamp[evicted_obj.key]
    del data_consistency_score[evicted_obj.key]