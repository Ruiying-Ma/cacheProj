# Import anything you need below
import time
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_PREDICTIVE_SCORE = 1.0
FREQUENCY_WEIGHT = 0.5
RECENCY_WEIGHT = 0.5
TREND_ADJUSTMENT_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive score for each cache entry, a global access pattern trend, and a synchronization timestamp. The predictive score is calculated using a combination of recent access frequency, recency, and a machine learning model that predicts future access likelihood. The global access pattern trend is updated based on overall cache access patterns, and the synchronization timestamp ensures consistency across distributed cache nodes.
predictive_scores = defaultdict(lambda: INITIAL_PREDICTIVE_SCORE)
access_frequencies = defaultdict(int)
last_access_times = defaultdict(int)
global_access_pattern_trend = 0.0
synchronization_timestamp = time.time()

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest predictive score, adjusted by the global access pattern trend. This ensures that entries with low likelihood of future access are prioritized for eviction, while also considering the overall access trends to adapt to changing workloads.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = predictive_scores[key] - global_access_pattern_trend
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive score of the accessed entry is increased based on its recency and frequency of access. The global access pattern trend is updated to reflect the increased likelihood of similar accesses, and the synchronization timestamp is refreshed to maintain consistency across nodes.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    access_frequencies[obj.key] += 1
    last_access_times[obj.key] = cache_snapshot.access_count
    
    # Update predictive score
    predictive_scores[obj.key] = (FREQUENCY_WEIGHT * access_frequencies[obj.key] +
                                  RECENCY_WEIGHT * (cache_snapshot.access_count - last_access_times[obj.key]))
    
    # Update global access pattern trend
    global global_access_pattern_trend
    global_access_pattern_trend += TREND_ADJUSTMENT_FACTOR
    
    # Refresh synchronization timestamp
    global synchronization_timestamp
    synchronization_timestamp = time.time()

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its predictive score based on initial access patterns and the global trend. The global access pattern trend is adjusted to account for the new entry, and the synchronization timestamp is updated to ensure all nodes are aware of the new insertion.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Initialize predictive score
    predictive_scores[obj.key] = INITIAL_PREDICTIVE_SCORE
    
    # Adjust global access pattern trend
    global global_access_pattern_trend
    global_access_pattern_trend += TREND_ADJUSTMENT_FACTOR
    
    # Update synchronization timestamp
    global synchronization_timestamp
    synchronization_timestamp = time.time()

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the global access pattern trend to reflect the removal of the entry. The synchronization timestamp is updated to maintain consistency across distributed nodes, ensuring all nodes are synchronized with the current cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Recalibrate global access pattern trend
    global global_access_pattern_trend
    global_access_pattern_trend -= TREND_ADJUSTMENT_FACTOR
    
    # Update synchronization timestamp
    global synchronization_timestamp
    synchronization_timestamp = time.time()