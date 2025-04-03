# Import anything you need below
import math

# Put tunable constant parameters below
BASE_ENTROPY_SCORE = 1.0
STABILIZATION_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive profile for each cache entry, an entropy score for access patterns, a stabilization factor for dynamic adjustments, and a temporal map of recent access times.
predictive_profiles = {}
entropy_scores = {}
temporal_map = {}
stabilization_factor = STABILIZATION_FACTOR

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest predictive profile score, adjusted by its entropy score and stabilization factor, prioritizing entries with older temporal insights.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        profile_score = predictive_profiles.get(key, 0)
        entropy_score = entropy_scores.get(key, BASE_ENTROPY_SCORE)
        last_access_time = temporal_map.get(key, 0)
        
        # Calculate the adjusted score
        adjusted_score = profile_score + entropy_score * stabilization_factor
        # Prioritize older temporal insights
        adjusted_score -= (cache_snapshot.access_count - last_access_time)
        
        if adjusted_score < min_score:
            min_score = adjusted_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive profile of the accessed entry is updated to reflect increased likelihood of future access, its entropy score is recalculated to capture recent access patterns, and the temporal map is updated with the current access time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    # Update predictive profile
    predictive_profiles[key] = predictive_profiles.get(key, 0) + 1
    # Recalculate entropy score
    entropy_scores[key] = math.log1p(predictive_profiles[key])
    # Update temporal map
    temporal_map[key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its predictive profile based on initial access context, sets a baseline entropy score, and records the current time in the temporal map, while adjusting the stabilization factor to accommodate the new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    # Initialize predictive profile
    predictive_profiles[key] = 1
    # Set baseline entropy score
    entropy_scores[key] = BASE_ENTROPY_SCORE
    # Record current time in temporal map
    temporal_map[key] = cache_snapshot.access_count
    # Adjust stabilization factor
    global stabilization_factor
    stabilization_factor += STABILIZATION_FACTOR / len(cache_snapshot.cache)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the stabilization factor to reflect the reduced cache size, updates the entropy mapping to account for the removed entry, and adjusts the predictive profiles of remaining entries to maintain balance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Remove evicted object's metadata
    predictive_profiles.pop(evicted_key, None)
    entropy_scores.pop(evicted_key, None)
    temporal_map.pop(evicted_key, None)
    # Recalibrate stabilization factor
    global stabilization_factor
    stabilization_factor -= STABILIZATION_FACTOR / (len(cache_snapshot.cache) + 1)
    # Adjust predictive profiles of remaining entries
    for key in cache_snapshot.cache:
        predictive_profiles[key] = max(0, predictive_profiles[key] - 1)