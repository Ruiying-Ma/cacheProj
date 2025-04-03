# Import anything you need below
import math

# Put tunable constant parameters below
GRADIENT_WEIGHT = 0.5
FREQUENCY_WEIGHT = 0.5
BASELINE_FREQUENCY_SCORE = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a gradient vector for each cache entry to track access patterns, a frequency coherence score to measure access consistency, and a dynamic priority score that combines heuristic optimization and recent access frequency.
metadata = {
    'gradient_vectors': {},  # Maps obj.key to its gradient vector magnitude
    'frequency_scores': {},  # Maps obj.key to its frequency coherence score
    'priority_scores': {}    # Maps obj.key to its dynamic priority score
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest dynamic priority score, which is calculated using a weighted combination of the gradient vector magnitude and frequency coherence score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_priority_score = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        priority_score = metadata['priority_scores'].get(key, float('inf'))
        if priority_score < min_priority_score:
            min_priority_score = priority_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the gradient vector for the accessed entry is updated to reflect the direction and magnitude of recent access changes, the frequency coherence score is incremented to reinforce consistent access, and the dynamic priority score is recalculated.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    # Update gradient vector
    metadata['gradient_vectors'][key] = metadata['gradient_vectors'].get(key, 0) + 1
    # Update frequency coherence score
    metadata['frequency_scores'][key] = metadata['frequency_scores'].get(key, BASELINE_FREQUENCY_SCORE) + 1
    # Recalculate dynamic priority score
    gradient_magnitude = metadata['gradient_vectors'][key]
    frequency_score = metadata['frequency_scores'][key]
    metadata['priority_scores'][key] = (GRADIENT_WEIGHT * gradient_magnitude) + (FREQUENCY_WEIGHT * frequency_score)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its gradient vector to zero, sets its frequency coherence score to a baseline value, and calculates its initial dynamic priority score based on heuristic optimization.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    # Initialize gradient vector to zero
    metadata['gradient_vectors'][key] = 0
    # Set frequency coherence score to baseline value
    metadata['frequency_scores'][key] = BASELINE_FREQUENCY_SCORE
    # Calculate initial dynamic priority score
    metadata['priority_scores'][key] = (GRADIENT_WEIGHT * metadata['gradient_vectors'][key]) + (FREQUENCY_WEIGHT * metadata['frequency_scores'][key])

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy adjusts the gradient vectors of remaining entries to account for the removal, recalibrates frequency coherence scores to maintain balance, and updates dynamic priority scores to reflect the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    # Remove metadata for evicted object
    if evicted_key in metadata['gradient_vectors']:
        del metadata['gradient_vectors'][evicted_key]
    if evicted_key in metadata['frequency_scores']:
        del metadata['frequency_scores'][evicted_key]
    if evicted_key in metadata['priority_scores']:
        del metadata['priority_scores'][evicted_key]
    
    # Adjust remaining entries
    for key in cache_snapshot.cache:
        # Recalculate dynamic priority scores
        gradient_magnitude = metadata['gradient_vectors'].get(key, 0)
        frequency_score = metadata['frequency_scores'].get(key, BASELINE_FREQUENCY_SCORE)
        metadata['priority_scores'][key] = (GRADIENT_WEIGHT * gradient_magnitude) + (FREQUENCY_WEIGHT * frequency_score)