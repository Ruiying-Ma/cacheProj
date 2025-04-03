# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
DEFAULT_FREQUENCY = 1
DEFAULT_RECENCY = 1
BASELINE_HEURISTIC_SCORE = 1.0
FREQUENCY_WEIGHT = 0.7
RECENCY_WEIGHT = 0.3

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive index for each cache entry, encapsulating historical access patterns, frequency, and recency. It also tracks a heuristic score that combines these factors to estimate future access likelihood.
cache_metadata = {
    'frequency': defaultdict(lambda: DEFAULT_FREQUENCY),
    'recency': defaultdict(lambda: DEFAULT_RECENCY),
    'heuristic_score': defaultdict(lambda: BASELINE_HEURISTIC_SCORE)
}

def calculate_heuristic_score(frequency, recency):
    return FREQUENCY_WEIGHT * frequency + RECENCY_WEIGHT * recency

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the cache entry with the lowest heuristic score, indicating the least likelihood of future access. This decision is optimized by algorithmically synthesizing historical data and predictive indexing.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        score = cache_metadata['heuristic_score'][key]
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the predictive index by increasing the frequency count and adjusting the recency factor. The heuristic score is recalculated to reflect the increased likelihood of future access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    cache_metadata['frequency'][key] += 1
    cache_metadata['recency'][key] = cache_snapshot.access_count
    cache_metadata['heuristic_score'][key] = calculate_heuristic_score(
        cache_metadata['frequency'][key],
        cache_metadata['recency'][key]
    )

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its predictive index with default values based on typical access patterns. The heuristic score is set to a baseline level, ready to be adjusted with future accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    cache_metadata['frequency'][key] = DEFAULT_FREQUENCY
    cache_metadata['recency'][key] = cache_snapshot.access_count
    cache_metadata['heuristic_score'][key] = BASELINE_HEURISTIC_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the predictive index and heuristic scores of remaining entries to ensure they accurately reflect the current cache state and access trends, potentially adjusting baseline assumptions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in cache_metadata['frequency']:
        del cache_metadata['frequency'][evicted_key]
    if evicted_key in cache_metadata['recency']:
        del cache_metadata['recency'][evicted_key]
    if evicted_key in cache_metadata['heuristic_score']:
        del cache_metadata['heuristic_score'][evicted_key]

    # Recalibrate heuristic scores for remaining entries
    for key in cache_snapshot.cache:
        cache_metadata['heuristic_score'][key] = calculate_heuristic_score(
            cache_metadata['frequency'][key],
            cache_metadata['recency'][key]
        )