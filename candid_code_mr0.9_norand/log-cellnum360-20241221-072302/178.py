# Import anything you need below
import numpy as np
from collections import defaultdict, deque

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for updating priority scores
BETA = 0.5   # Weight for predictive model adjustment

# Put the metadata specifically maintained by the policy below. The policy maintains a temporal access pattern matrix, dynamic priority scores for each cache entry, and a predictive model for future access patterns. It also keeps a synchronized execution log to ensure consistency across cache operations.
temporal_access_matrix = defaultdict(lambda: deque(maxlen=10))  # Stores recent access times for each object
priority_scores = defaultdict(float)  # Dynamic priority scores for each object
predictive_model = defaultdict(float)  # Predictive model for future access patterns
execution_log = []  # Synchronized execution log

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by interpolating temporal access patterns to predict future access likelihood, dynamically adjusting priority scores, and choosing the entry with the lowest predicted future access probability.
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
        # Predict future access probability
        future_access_prob = predictive_model[key]
        # Calculate score
        score = ALPHA * priority_scores[key] + BETA * future_access_prob
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the temporal access pattern matrix to reflect the recent access, recalibrates the dynamic priority score of the accessed entry, and refines the predictive model using the synchronized execution log.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    # Update temporal access pattern
    temporal_access_matrix[obj.key].append(cache_snapshot.access_count)
    
    # Recalibrate priority score
    priority_scores[obj.key] = len(temporal_access_matrix[obj.key])
    
    # Refine predictive model
    predictive_model[obj.key] = np.mean(temporal_access_matrix[obj.key])
    
    # Log the hit
    execution_log.append(('hit', obj.key, cache_snapshot.access_count))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its temporal access pattern and dynamic priority score, updates the predictive model to incorporate the new entry, and logs the insertion in the synchronized execution log.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    # Initialize temporal access pattern
    temporal_access_matrix[obj.key].append(cache_snapshot.access_count)
    
    # Initialize priority score
    priority_scores[obj.key] = 1
    
    # Update predictive model
    predictive_model[obj.key] = 1.0
    
    # Log the insertion
    execution_log.append(('insert', obj.key, cache_snapshot.access_count))

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the evicted entry's data from the temporal access pattern matrix, adjusts the predictive model to account for the change, and records the eviction in the synchronized execution log.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    # Remove evicted entry's data
    if evicted_obj.key in temporal_access_matrix:
        del temporal_access_matrix[evicted_obj.key]
    if evicted_obj.key in priority_scores:
        del priority_scores[evicted_obj.key]
    if evicted_obj.key in predictive_model:
        del predictive_model[evicted_obj.key]
    
    # Log the eviction
    execution_log.append(('evict', evicted_obj.key, cache_snapshot.access_count))