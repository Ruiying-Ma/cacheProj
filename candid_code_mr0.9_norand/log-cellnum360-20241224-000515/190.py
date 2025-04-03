# Import anything you need below
from collections import defaultdict, deque

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.7
RECENCY_WEIGHT = 0.3
HIGH_PRIORITY_RATIO = 0.7

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive filter that uses historical access patterns to estimate future access likelihood, a priority score for each cache entry based on access frequency and recency, an adaptive partition that dynamically allocates cache space between high-priority and low-priority items, and heuristic tuning parameters that adjust the sensitivity of the predictive filter and priority enhancer.
access_frequency = defaultdict(int)
access_recency = {}
priority_scores = {}
high_priority_keys = set()
low_priority_keys = set()
access_history = deque(maxlen=1000)  # Keep a history of accesses for predictive filtering

def calculate_priority_score(key):
    frequency = access_frequency[key]
    recency = access_recency[key]
    return FREQUENCY_WEIGHT * frequency + RECENCY_WEIGHT * recency

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first checking the adaptive partition to determine if the item belongs to the high-priority or low-priority section. Within the selected section, it uses the predictive filter to identify items with the lowest future access likelihood and the priority enhancer to break ties by selecting the item with the lowest priority score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Determine which section to evict from
    if cache_snapshot.size + obj.size > cache_snapshot.capacity * HIGH_PRIORITY_RATIO:
        # Evict from low-priority section
        candidates = low_priority_keys
    else:
        # Evict from high-priority section
        candidates = high_priority_keys

    # Find the candidate with the lowest priority score
    min_score = float('inf')
    for key in candidates:
        score = priority_scores[key]
        if score < min_score:
            min_score = score
            candid_obj_key = key

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the priority score of the accessed item by increasing its recency and frequency components. The predictive filter is also updated to reflect the new access pattern, and heuristic tuning parameters are adjusted to optimize future predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] += 1
    access_recency[key] = cache_snapshot.access_count
    priority_scores[key] = calculate_priority_score(key)
    access_history.append(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial priority score based on the object's predicted access likelihood and updates the adaptive partition to ensure balanced space allocation. The predictive filter is recalibrated to incorporate the new object's access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] = 1
    access_recency[key] = cache_snapshot.access_count
    priority_scores[key] = calculate_priority_score(key)
    access_history.append(key)

    # Update adaptive partition
    if cache_snapshot.size <= cache_snapshot.capacity * HIGH_PRIORITY_RATIO:
        high_priority_keys.add(key)
    else:
        low_priority_keys.add(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the predictive filter to remove the evicted item's influence on future predictions. The adaptive partition is adjusted to reflect the change in cache composition, and heuristic tuning parameters are fine-tuned to maintain optimal performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in high_priority_keys:
        high_priority_keys.remove(evicted_key)
    if evicted_key in low_priority_keys:
        low_priority_keys.remove(evicted_key)

    # Remove evicted item from metadata
    if evicted_key in access_frequency:
        del access_frequency[evicted_key]
    if evicted_key in access_recency:
        del access_recency[evicted_key]
    if evicted_key in priority_scores:
        del priority_scores[evicted_key]

    # Recalibrate predictive filter
    if evicted_key in access_history:
        access_history.remove(evicted_key)