# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_ACCESS_FREQUENCY = 1
BASELINE_ENERGY_COST = 1.0
CONTEXTUAL_IMPORTANCE_WEIGHT = 0.5
ENERGY_COST_WEIGHT = 0.3
RECENCY_WEIGHT = 0.1
FREQUENCY_WEIGHT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency, energy cost of accessing data, and contextual tags that describe the data's usage patterns and importance.
metadata = {
    'access_frequency': defaultdict(int),
    'recency': {},
    'energy_cost': defaultdict(lambda: BASELINE_ENERGY_COST),
    'contextual_tags': defaultdict(lambda: {'importance': 1.0})
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by evaluating a composite score that combines low access frequency, low recency, high energy cost, and low contextual importance, ensuring that the least impactful data is removed.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        frequency = metadata['access_frequency'][key]
        recency = metadata['recency'][key]
        energy_cost = metadata['energy_cost'][key]
        importance = metadata['contextual_tags'][key]['importance']
        
        score = (FREQUENCY_WEIGHT * frequency +
                 RECENCY_WEIGHT * recency +
                 ENERGY_COST_WEIGHT * energy_cost -
                 CONTEXTUAL_IMPORTANCE_WEIGHT * importance)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the access frequency, updates the recency timestamp, and refines the contextual tags based on the current usage pattern, while also adjusting the energy cost based on recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['recency'][key] = cache_snapshot.access_count
    # Adjust energy cost and contextual tags based on some heuristic
    metadata['energy_cost'][key] *= 0.9  # Example: reduce energy cost slightly
    metadata['contextual_tags'][key]['importance'] *= 1.1  # Example: increase importance

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its metadata with a baseline access frequency, current timestamp for recency, estimated energy cost, and contextual tags derived from initial access context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = BASELINE_ACCESS_FREQUENCY
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['energy_cost'][key] = BASELINE_ENERGY_COST
    metadata['contextual_tags'][key] = {'importance': 1.0}  # Initial importance

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the energy optimization parameters and contextual intelligence algorithms to improve future eviction decisions, while also updating the overall cache usage statistics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Remove metadata for the evicted object
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['recency']:
        del metadata['recency'][evicted_key]
    if evicted_key in metadata['energy_cost']:
        del metadata['energy_cost'][evicted_key]
    if evicted_key in metadata['contextual_tags']:
        del metadata['contextual_tags'][evicted_key]
    
    # Recalibrate energy optimization parameters and contextual intelligence algorithms
    # This is a placeholder for more complex recalibration logic
    for key in metadata['energy_cost']:
        metadata['energy_cost'][key] *= 1.05  # Example: slightly increase energy cost