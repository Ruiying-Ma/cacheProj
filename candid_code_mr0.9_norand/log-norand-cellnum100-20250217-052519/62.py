# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import defaultdict, deque

# Put tunable constant parameters below
INITIAL_ACCESS_LATENCY_SCORE = 100

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a predictive index for future access patterns, stratified data tiers based on access frequency, an access latency score for each cache entry, and a prefetching queue for anticipated data needs.
access_latency_scores = {}
access_frequencies = defaultdict(int)
predictive_index = {}
prefetching_queue = deque()

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache entry with the lowest access latency score within the least frequently accessed data tier, while also considering the predictive index to avoid evicting data likely to be accessed soon.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_latency_score = float('inf')
    min_frequency = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        frequency = access_frequencies[key]
        latency_score = access_latency_scores[key]
        
        if frequency < min_frequency or (frequency == min_frequency and latency_score < min_latency_score):
            if key not in predictive_index or predictive_index[key] > cache_snapshot.access_count:
                min_frequency = frequency
                min_latency_score = latency_score
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access latency score to reflect the reduced latency, adjusts the data stratification to potentially move the entry to a higher frequency tier, and updates the predictive index to refine future access predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    access_frequencies[key] += 1
    access_latency_scores[key] = max(1, access_latency_scores[key] - 1)
    predictive_index[key] = cache_snapshot.access_count + 10  # Example prediction logic

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access latency score, places it in the appropriate data tier based on initial access frequency, and updates the predictive index and prefetching queue to account for the new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    access_frequencies[key] = 1
    access_latency_scores[key] = INITIAL_ACCESS_LATENCY_SCORE
    predictive_index[key] = cache_snapshot.access_count + 10  # Example prediction logic
    prefetching_queue.append(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the entry from the predictive index, adjusts the data stratification to reflect the removal, and updates the access latency scores of remaining entries if necessary to maintain accurate latency tracking.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in access_frequencies:
        del access_frequencies[evicted_key]
    if evicted_key in access_latency_scores:
        del access_latency_scores[evicted_key]
    if evicted_key in predictive_index:
        del predictive_index[evicted_key]
    if evicted_key in prefetching_queue:
        prefetching_queue.remove(evicted_key)