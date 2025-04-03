# Import anything you need below
from collections import defaultdict, deque
import math

# Put tunable constant parameters below
ALPHA = 0.7  # Smoothing factor for frequency count
BETA = 0.3   # Weight for recency in prediction score
GAMMA = 0.5  # Weight for frequency in prediction score

# Put the metadata specifically maintained by the policy below. The policy maintains a time-series of access patterns for each cache entry, a noise-reduced prediction score for future accesses, and a smoothed frequency count. It also extracts features such as recency, frequency, and temporal locality from the access patterns.
access_time_series = defaultdict(deque)  # Stores access times for each object
prediction_scores = defaultdict(float)   # Stores prediction scores for each object
smoothed_frequency = defaultdict(float)  # Stores smoothed frequency counts for each object

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by predicting future access patterns using the noise-reduced prediction score. It selects the entry with the lowest predicted future access likelihood, considering both the smoothed frequency count and extracted features.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = prediction_scores[key]
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the time-series with the latest access, recalculates the noise-reduced prediction score, and adjusts the smoothed frequency count. It also re-evaluates the extracted features to refine future predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Update time-series
    access_time_series[key].append(current_time)
    
    # Update smoothed frequency count
    smoothed_frequency[key] = ALPHA * smoothed_frequency[key] + (1 - ALPHA)
    
    # Recalculate prediction score
    recency = current_time - access_time_series[key][-1]
    frequency = smoothed_frequency[key]
    prediction_scores[key] = BETA * (1 / (1 + recency)) + GAMMA * frequency

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the time-series with the current access, sets an initial prediction score, and establishes a baseline smoothed frequency count. It extracts initial features to start tracking the object's access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Initialize time-series
    access_time_series[key] = deque([current_time])
    
    # Set initial smoothed frequency count
    smoothed_frequency[key] = 1.0
    
    # Set initial prediction score
    prediction_scores[key] = BETA * (1 / (1 + current_time)) + GAMMA * smoothed_frequency[key]

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the time-series data for the evicted entry, recalibrates the prediction scores for remaining entries, and adjusts the smoothed frequency counts to reflect the updated cache state. It also re-assesses the feature set for the remaining entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove time-series data for evicted entry
    if evicted_key in access_time_series:
        del access_time_series[evicted_key]
    if evicted_key in prediction_scores:
        del prediction_scores[evicted_key]
    if evicted_key in smoothed_frequency:
        del smoothed_frequency[evicted_key]
    
    # Recalibrate prediction scores and smoothed frequency counts for remaining entries
    for key in cache_snapshot.cache:
        update_after_hit(cache_snapshot, cache_snapshot.cache[key])