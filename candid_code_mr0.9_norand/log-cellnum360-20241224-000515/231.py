# Import anything you need below
from collections import defaultdict
import math

# Put tunable constant parameters below
HEURISTIC_WEIGHT = 0.7
PREDICTIVE_WEIGHT = 0.3
BASELINE_PROBABILITY = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a heuristic score for each cache entry, a temporal access pattern log, and a predictive access probability score. The heuristic score is derived from a combination of recent access frequency and recency, while the temporal log records timestamps of accesses. The predictive score estimates future access likelihood based on historical patterns.
heuristic_scores = defaultdict(float)
temporal_logs = defaultdict(list)
predictive_scores = defaultdict(float)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest combined heuristic and predictive score. It considers both the immediate past access patterns and the predicted future access likelihood, ensuring that entries with low probability of future access and low recent access frequency are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (HEURISTIC_WEIGHT * heuristic_scores[key] + 
                          PREDICTIVE_WEIGHT * predictive_scores[key])
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the heuristic score by increasing it based on the recency and frequency of access. The temporal log is updated with the current timestamp, and the predictive score is recalibrated using the updated access pattern to refine future access predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Update heuristic score
    heuristic_scores[key] += 1 / (current_time - temporal_logs[key][-1] + 1)
    
    # Update temporal log
    temporal_logs[key].append(current_time)
    
    # Recalibrate predictive score
    predictive_scores[key] = min(1.0, predictive_scores[key] + 0.05)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the heuristic score based on initial access frequency and recency assumptions. The temporal log is started with the current timestamp, and the predictive score is set using a baseline probability derived from similar past entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Initialize heuristic score
    heuristic_scores[key] = 1.0
    
    # Initialize temporal log
    temporal_logs[key] = [current_time]
    
    # Set predictive score
    predictive_scores[key] = BASELINE_PROBABILITY

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy adjusts the heuristic scores of remaining entries to reflect the change in cache dynamics. The temporal logs are reviewed to ensure they accurately represent the current state, and predictive scores are recalibrated to account for the removal of the evicted entry, potentially increasing the predicted access likelihood of similar entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove metadata of evicted object
    if evicted_key in heuristic_scores:
        del heuristic_scores[evicted_key]
    if evicted_key in temporal_logs:
        del temporal_logs[evicted_key]
    if evicted_key in predictive_scores:
        del predictive_scores[evicted_key]
    
    # Adjust heuristic scores and predictive scores of remaining entries
    for key in cache_snapshot.cache:
        heuristic_scores[key] *= 0.9  # Decay heuristic score
        predictive_scores[key] = min(1.0, predictive_scores[key] + 0.01)  # Slightly increase predictive score