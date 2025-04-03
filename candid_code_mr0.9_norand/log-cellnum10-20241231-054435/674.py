# Import anything you need below
import math
from collections import defaultdict

# Put tunable constant parameters below
BASE_ENTROPY_SCORE = 1.0
BASE_TEMPORAL_SYNERGY_SCORE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a symmetric matrix to track access patterns, an entropy score for each cache entry to measure access unpredictability, a temporal synergy score to capture time-based access correlations, and a heuristic score that integrates these factors.
access_matrix = defaultdict(lambda: defaultdict(int))
entropy_scores = defaultdict(float)
temporal_synergy_scores = defaultdict(float)
heuristic_scores = defaultdict(float)
last_access_time = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the highest entropy score, indicating the least predictable access pattern, while considering the lowest temporal synergy score to ensure minimal impact on time-based access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_heuristic_score = -math.inf

    for key, cached_obj in cache_snapshot.cache.items():
        heuristic_score = entropy_scores[key] - temporal_synergy_scores[key]
        if heuristic_score > max_heuristic_score:
            max_heuristic_score = heuristic_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the symmetric matrix to reflect the latest access pattern, recalculates the entropy score to account for the new access, adjusts the temporal synergy score based on the time since the last access, and updates the heuristic score to integrate these changes.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    obj_key = obj.key

    # Update access matrix
    for key in cache_snapshot.cache:
        if key != obj_key:
            access_matrix[obj_key][key] += 1
            access_matrix[key][obj_key] += 1

    # Recalculate entropy score
    total_accesses = sum(access_matrix[obj_key].values())
    entropy = -sum((count / total_accesses) * math.log(count / total_accesses) for count in access_matrix[obj_key].values() if count > 0)
    entropy_scores[obj_key] = entropy

    # Adjust temporal synergy score
    time_since_last_access = current_time - last_access_time[obj_key]
    temporal_synergy_scores[obj_key] = BASE_TEMPORAL_SYNERGY_SCORE / (1 + time_since_last_access)

    # Update heuristic score
    heuristic_scores[obj_key] = entropy_scores[obj_key] - temporal_synergy_scores[obj_key]

    # Update last access time
    last_access_time[obj_key] = current_time

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its symmetric matrix entry, assigns a baseline entropy score, calculates an initial temporal synergy score based on recent access patterns, and computes an initial heuristic score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    obj_key = obj.key
    current_time = cache_snapshot.access_count

    # Initialize symmetric matrix entry
    for key in cache_snapshot.cache:
        access_matrix[obj_key][key] = 0
        access_matrix[key][obj_key] = 0

    # Assign baseline entropy score
    entropy_scores[obj_key] = BASE_ENTROPY_SCORE

    # Calculate initial temporal synergy score
    temporal_synergy_scores[obj_key] = BASE_TEMPORAL_SYNERGY_SCORE

    # Compute initial heuristic score
    heuristic_scores[obj_key] = entropy_scores[obj_key] - temporal_synergy_scores[obj_key]

    # Set last access time
    last_access_time[obj_key] = current_time

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the evicted entry's metadata from the symmetric matrix, recalibrates the entropy scores of remaining entries, adjusts their temporal synergy scores to reflect the change, and updates the heuristic scores accordingly.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key

    # Remove evicted entry's metadata from the symmetric matrix
    del access_matrix[evicted_key]
    for key in access_matrix:
        if evicted_key in access_matrix[key]:
            del access_matrix[key][evicted_key]

    # Recalibrate entropy scores of remaining entries
    for key in cache_snapshot.cache:
        total_accesses = sum(access_matrix[key].values())
        if total_accesses > 0:
            entropy = -sum((count / total_accesses) * math.log(count / total_accesses) for count in access_matrix[key].values() if count > 0)
            entropy_scores[key] = entropy
        else:
            entropy_scores[key] = BASE_ENTROPY_SCORE

    # Adjust temporal synergy scores
    for key in cache_snapshot.cache:
        time_since_last_access = cache_snapshot.access_count - last_access_time[key]
        temporal_synergy_scores[key] = BASE_TEMPORAL_SYNERGY_SCORE / (1 + time_since_last_access)

    # Update heuristic scores
    for key in cache_snapshot.cache:
        heuristic_scores[key] = entropy_scores[key] - temporal_synergy_scores[key]