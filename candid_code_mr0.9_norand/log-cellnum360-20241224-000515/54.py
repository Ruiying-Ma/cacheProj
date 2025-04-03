# Import anything you need below
from collections import deque, defaultdict

# Put tunable constant parameters below
SLEEP_THRESHOLD = 5  # Number of accesses before an entry can go to sleep
SCORE_DECREMENT = 1  # Amount to decrease the eviction score on hit
INITIAL_SCORE = 10   # Initial score for a new entry

# Put the metadata specifically maintained by the policy below. The policy maintains a rotating queue of cache entries, a sleep-wake status for each entry, an adaptive eviction score based on access patterns, and a sequential access counter.
rotating_queue = deque()
sleep_wake_status = {}
eviction_scores = defaultdict(lambda: INITIAL_SCORE)
sequential_access_counter = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the highest adaptive eviction score, prioritizing entries in sleep mode, and considering sequential access patterns to avoid evicting entries that are part of a recent sequence.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_score = -1

    for key in rotating_queue:
        if sleep_wake_status[key] == 'sleep' or sequential_access_counter[key] < SLEEP_THRESHOLD:
            score = eviction_scores[key]
            if score > max_score:
                max_score = score
                candid_obj_key = key

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the entry is moved to the back of the rotating queue, its sleep-wake status is set to wake, its adaptive eviction score is decreased, and its sequential access counter is incremented.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    if key in rotating_queue:
        rotating_queue.remove(key)
    rotating_queue.append(key)
    sleep_wake_status[key] = 'wake'
    eviction_scores[key] = max(0, eviction_scores[key] - SCORE_DECREMENT)
    sequential_access_counter[key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is added to the back of the rotating queue, its sleep-wake status is set to wake, its adaptive eviction score is initialized based on initial access frequency, and its sequential access counter is set to zero.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    rotating_queue.append(key)
    sleep_wake_status[key] = 'wake'
    eviction_scores[key] = INITIAL_SCORE
    sequential_access_counter[key] = 0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the rotating queue is adjusted to maintain order, the sleep-wake status of remaining entries is evaluated for potential sleep transitions, and the adaptive eviction scores of remaining entries are recalibrated based on recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in rotating_queue:
        rotating_queue.remove(evicted_key)
    del sleep_wake_status[evicted_key]
    del eviction_scores[evicted_key]
    del sequential_access_counter[evicted_key]

    for key in rotating_queue:
        if sequential_access_counter[key] >= SLEEP_THRESHOLD:
            sleep_wake_status[key] = 'sleep'
        else:
            sleep_wake_status[key] = 'wake'
        # Recalibrate eviction scores if needed
        eviction_scores[key] = max(0, eviction_scores[key] - SCORE_DECREMENT)