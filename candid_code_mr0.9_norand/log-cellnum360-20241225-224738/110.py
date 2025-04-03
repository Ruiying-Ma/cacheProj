# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
LATENCY_SENSITIVITY_WEIGHT = 0.5
ACCESS_FREQUENCY_WEIGHT = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains a hierarchical index of cache entries, organized by access frequency and latency sensitivity. It also includes predictive scores for each entry, calculated using historical access patterns and resource allocation metrics.
cache_metadata = {
    'access_frequency': defaultdict(int),  # Tracks access frequency of each object
    'predictive_score': {},  # Predictive score for each object
    'latency_sensitivity': {},  # Latency sensitivity for each object
}

def calculate_predictive_score(obj_key):
    # Calculate predictive score based on access frequency and latency sensitivity
    frequency = cache_metadata['access_frequency'][obj_key]
    latency_sensitivity = cache_metadata['latency_sensitivity'].get(obj_key, 1)
    return (ACCESS_FREQUENCY_WEIGHT * frequency) - (LATENCY_SENSITIVITY_WEIGHT * latency_sensitivity)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest predictive score within the least frequently accessed tier of the hierarchical index, prioritizing entries with lower latency sensitivity.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for obj_key, cached_obj in cache_snapshot.cache.items():
        score = calculate_predictive_score(obj_key)
        if score < min_score:
            min_score = score
            candid_obj_key = obj_key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency and recalculates the predictive score for the accessed entry, promoting it within the hierarchical index if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    obj_key = obj.key
    cache_metadata['access_frequency'][obj_key] += 1
    cache_metadata['predictive_score'][obj_key] = calculate_predictive_score(obj_key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial predictive score based on current resource allocation and expected access patterns, placing it in the appropriate tier of the hierarchical index.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    obj_key = obj.key
    cache_metadata['access_frequency'][obj_key] = 1
    cache_metadata['latency_sensitivity'][obj_key] = 1  # Initial latency sensitivity
    cache_metadata['predictive_score'][obj_key] = calculate_predictive_score(obj_key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy adjusts the hierarchical index to reflect the removal and recalibrates predictive scores for remaining entries, considering the freed resources and potential changes in access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_obj_key = evicted_obj.key
    # Remove evicted object metadata
    if evicted_obj_key in cache_metadata['access_frequency']:
        del cache_metadata['access_frequency'][evicted_obj_key]
    if evicted_obj_key in cache_metadata['predictive_score']:
        del cache_metadata['predictive_score'][evicted_obj_key]
    if evicted_obj_key in cache_metadata['latency_sensitivity']:
        del cache_metadata['latency_sensitivity'][evicted_obj_key]
    
    # Recalculate predictive scores for remaining entries
    for obj_key in cache_snapshot.cache:
        cache_metadata['predictive_score'][obj_key] = calculate_predictive_score(obj_key)