# Import anything you need below
import time

# Put tunable constant parameters below
PREDICTIVE_SCORE_DECAY = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, and a predictive score derived from temporal analysis and pattern recognition of access patterns.
metadata = {
    'access_frequency': {},
    'last_access_time': {},
    'predictive_score': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a combination of the lowest predictive score and the longest time since last access, ensuring that items predicted to be less useful in the near future are evicted first.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    oldest_time = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = metadata['predictive_score'].get(key, float('inf'))
        last_access = metadata['last_access_time'].get(key, float('inf'))
        
        if score < min_score or (score == min_score and last_access < oldest_time):
            min_score = score
            oldest_time = last_access
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the last access time to the current time, increments the access frequency, and recalculates the predictive score using the updated access pattern data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    key = obj.key
    
    metadata['last_access_time'][key] = current_time
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    
    # Recalculate predictive score
    frequency = metadata['access_frequency'][key]
    last_access = metadata['last_access_time'][key]
    metadata['predictive_score'][key] = PREDICTIVE_SCORE_DECAY * (frequency / (current_time - last_access + 1))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the last access time to the current time, sets the access frequency to one, and calculates an initial predictive score based on the insertion context and historical data patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    key = obj.key
    
    metadata['last_access_time'][key] = current_time
    metadata['access_frequency'][key] = 1
    
    # Initial predictive score
    metadata['predictive_score'][key] = PREDICTIVE_SCORE_DECAY * (1 / (current_time + 1))

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the metadata associated with the evicted object and adjusts the predictive models to account for the change in the cache's content, ensuring future predictions remain accurate.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    if evicted_key in metadata['last_access_time']:
        del metadata['last_access_time'][evicted_key]
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['predictive_score']:
        del metadata['predictive_score'][evicted_key]