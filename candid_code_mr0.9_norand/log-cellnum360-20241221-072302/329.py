# Import anything you need below
import math
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_PREDICTIVE_SCORE = 1.0
NEUTRAL_MODULATION_FACTOR = 1.0
TIME_DECAY_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a vector for each cache entry representing its access pattern, a timestamp of the last access, a predictive score indicating future access likelihood, and a modulation factor that adjusts based on recent access trends.
cache_metadata = {
    'access_pattern': defaultdict(lambda: [0] * 10),  # Example vector size
    'last_access_time': {},
    'predictive_score': defaultdict(lambda: BASELINE_PREDICTIVE_SCORE),
    'modulation_factor': defaultdict(lambda: NEUTRAL_MODULATION_FACTOR)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by transforming the access pattern vectors into a priority score, factoring in the time since last access and predictive score. The entry with the lowest combined score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    lowest_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        # Calculate the time since last access
        time_since_last_access = cache_snapshot.access_count - cache_metadata['last_access_time'][key]
        
        # Calculate the priority score
        access_vector = cache_metadata['access_pattern'][key]
        predictive_score = cache_metadata['predictive_score'][key]
        modulation_factor = cache_metadata['modulation_factor'][key]
        
        # Example score calculation
        score = (sum(access_vector) * modulation_factor) / (predictive_score * (1 + TIME_DECAY_FACTOR * time_since_last_access))
        
        if score < lowest_score:
            lowest_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access pattern vector is updated to reflect the new access, the timestamp is refreshed, the predictive score is recalibrated using recent access data, and the modulation factor is adjusted to reflect any changes in access frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    # Update access pattern vector
    cache_metadata['access_pattern'][key].append(1)
    cache_metadata['access_pattern'][key] = cache_metadata['access_pattern'][key][-10:]  # Keep vector size constant
    
    # Refresh timestamp
    cache_metadata['last_access_time'][key] = cache_snapshot.access_count
    
    # Recalibrate predictive score
    cache_metadata['predictive_score'][key] = sum(cache_metadata['access_pattern'][key]) / len(cache_metadata['access_pattern'][key])
    
    # Adjust modulation factor
    cache_metadata['modulation_factor'][key] *= 1.1  # Example adjustment

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its access pattern vector is initialized, the current time is recorded as the last access time, a baseline predictive score is set, and the modulation factor is initialized to a neutral state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    # Initialize access pattern vector
    cache_metadata['access_pattern'][key] = [0] * 10
    
    # Record current time as last access time
    cache_metadata['last_access_time'][key] = cache_snapshot.access_count
    
    # Set baseline predictive score
    cache_metadata['predictive_score'][key] = BASELINE_PREDICTIVE_SCORE
    
    # Initialize modulation factor
    cache_metadata['modulation_factor'][key] = NEUTRAL_MODULATION_FACTOR

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the predictive scores of remaining entries based on the removed entry's data, adjusts modulation factors to account for the change in cache dynamics, and updates any global statistics used for vector transformations.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Remove metadata for evicted object
    del cache_metadata['access_pattern'][evicted_key]
    del cache_metadata['last_access_time'][evicted_key]
    del cache_metadata['predictive_score'][evicted_key]
    del cache_metadata['modulation_factor'][evicted_key]
    
    # Recalibrate predictive scores and modulation factors for remaining entries
    for key in cache_snapshot.cache:
        cache_metadata['predictive_score'][key] *= 0.9  # Example recalibration
        cache_metadata['modulation_factor'][key] *= 0.95  # Example adjustment