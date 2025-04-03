# Import anything you need below
import math
import time

# Put tunable constant parameters below
BASE_EXPONENTIAL_WEIGHT = 1.0
DECAY_RATE = 0.1
HEURISTIC_PRIORITY_BASE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry including a predictive decay score, an exponential access weight, a temporal access variance, and a heuristic priority score.
metadata = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the highest predictive decay score, adjusted by the exponential access weight and temporal access variance, and then further refined by the heuristic priority score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_score = -float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        score = (meta['predictive_decay_score'] * meta['exponential_access_weight'] / 
                 (meta['temporal_access_variance'] + 1)) + meta['heuristic_priority_score']
        if score > max_score:
            max_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive decay score is recalculated based on the current time and access pattern, the exponential access weight is increased, the temporal access variance is updated to reflect the new access time, and the heuristic priority score is adjusted based on recent access behavior.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    meta = metadata[obj.key]
    
    # Recalculate predictive decay score
    time_since_last_access = current_time - meta['last_access_time']
    meta['predictive_decay_score'] *= math.exp(-DECAY_RATE * time_since_last_access)
    
    # Increase exponential access weight
    meta['exponential_access_weight'] += BASE_EXPONENTIAL_WEIGHT
    
    # Update temporal access variance
    meta['temporal_access_variance'] = ((meta['temporal_access_variance'] * (meta['access_count'] - 1) + 
                                         time_since_last_access ** 2) / meta['access_count'])
    
    # Adjust heuristic priority score
    meta['heuristic_priority_score'] += HEURISTIC_PRIORITY_BASE / (meta['access_count'] + 1)
    
    # Update last access time and access count
    meta['last_access_time'] = current_time
    meta['access_count'] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the predictive decay score is initialized, the exponential access weight is set to a base value, the temporal access variance is calculated from the insertion time, and the heuristic priority score is set based on initial access predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    metadata[obj.key] = {
        'predictive_decay_score': 1.0,
        'exponential_access_weight': BASE_EXPONENTIAL_WEIGHT,
        'temporal_access_variance': 0.0,
        'heuristic_priority_score': HEURISTIC_PRIORITY_BASE,
        'last_access_time': current_time,
        'access_count': 1
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalculates the predictive decay scores for remaining entries, adjusts the exponential access weights to reflect the new cache state, updates the temporal access variances, and recalibrates the heuristic priority scores to maintain optimal cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    del metadata[evicted_obj.key]
    
    for key, meta in metadata.items():
        time_since_last_access = current_time - meta['last_access_time']
        
        # Recalculate predictive decay score
        meta['predictive_decay_score'] *= math.exp(-DECAY_RATE * time_since_last_access)
        
        # Adjust exponential access weight
        meta['exponential_access_weight'] = max(BASE_EXPONENTIAL_WEIGHT, meta['exponential_access_weight'] - 0.1)
        
        # Update temporal access variance
        meta['temporal_access_variance'] = ((meta['temporal_access_variance'] * (meta['access_count'] - 1) + 
                                             time_since_last_access ** 2) / meta['access_count'])
        
        # Recalibrate heuristic priority score
        meta['heuristic_priority_score'] = HEURISTIC_PRIORITY_BASE / (meta['access_count'] + 1)