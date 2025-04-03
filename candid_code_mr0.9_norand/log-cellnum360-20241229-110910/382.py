# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
CAUSAL_SCORE_INCREMENT = 1
HIGH_HARMONY_INDEX_INCREMENT = 2
NEUTRAL_HARMONY_INDEX = 0.5
REACTIVE_INTEGRATION_ADJUSTMENT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a 'Causal Score' for each cache entry, which is a composite measure derived from access frequency, recency, and a 'Harmony Index' that reflects the entry's role in maintaining systematic harmony within the cache. Additionally, a 'Reactive Integration Factor' is tracked to assess the entry's adaptability to changing access patterns.
metadata = {
    'causal_score': defaultdict(lambda: 0),
    'harmony_index': defaultdict(lambda: NEUTRAL_HARMONY_INDEX),
    'reactive_integration_factor': defaultdict(lambda: 0)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest Causal Score, prioritizing those with a low Harmony Index and Reactive Integration Factor. This ensures that entries contributing least to the cache's overall efficiency and adaptability are removed.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = metadata['causal_score'][key]
        harmony_index = metadata['harmony_index'][key]
        reactive_integration = metadata['reactive_integration_factor'][key]
        
        # Calculate a composite score for eviction decision
        composite_score = score + harmony_index + reactive_integration
        
        if composite_score < min_score:
            min_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Causal Score of the accessed entry is incremented, with a greater increase if the entry has a high Harmony Index. The Reactive Integration Factor is adjusted to reflect the entry's improved adaptability to current access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    harmony_index = metadata['harmony_index'][key]
    
    # Increment Causal Score
    increment = CAUSAL_SCORE_INCREMENT
    if harmony_index > NEUTRAL_HARMONY_INDEX:
        increment += HIGH_HARMONY_INDEX_INCREMENT
    
    metadata['causal_score'][key] += increment
    
    # Adjust Reactive Integration Factor
    metadata['reactive_integration_factor'][key] += REACTIVE_INTEGRATION_ADJUSTMENT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its Causal Score is initialized based on its initial access frequency and predicted role in systematic harmony. The Harmony Index is set to a neutral value, and the Reactive Integration Factor is calibrated to anticipate potential access pattern shifts.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    
    # Initialize Causal Score
    metadata['causal_score'][key] = 1  # Initial access frequency
    
    # Set Harmony Index to neutral
    metadata['harmony_index'][key] = NEUTRAL_HARMONY_INDEX
    
    # Calibrate Reactive Integration Factor
    metadata['reactive_integration_factor'][key] = REACTIVE_INTEGRATION_ADJUSTMENT

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the Harmony Index of remaining entries to ensure systematic balance. The Reactive Integration Factor of all entries is slightly adjusted to reflect the cache's new state, promoting adaptability to future access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        # Recalibrate Harmony Index
        metadata['harmony_index'][key] = NEUTRAL_HARMONY_INDEX
        
        # Adjust Reactive Integration Factor
        metadata['reactive_integration_factor'][key] += REACTIVE_INTEGRATION_ADJUSTMENT