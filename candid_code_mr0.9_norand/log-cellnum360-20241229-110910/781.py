# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_SYNAPTIC_STRENGTH = 1
SPATIAL_ALIGNMENT_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a 'Neural Pathway Map' that records access patterns as pathways, 'Synaptic Strength' indicating the frequency of access, 'Temporal Distortion Factor' to track the recency of access, and 'Spatial Alignment Score' to measure the spatial locality of data.
neural_pathway_map = {
    'synaptic_strength': defaultdict(lambda: BASELINE_SYNAPTIC_STRENGTH),
    'temporal_distortion': {},
    'spatial_alignment': defaultdict(float)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the cache entry with the lowest combined score of Synaptic Strength, Temporal Distortion Factor, and Spatial Alignment Score, simulating a weakened neural pathway.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        synaptic_strength = neural_pathway_map['synaptic_strength'][key]
        temporal_distortion = cache_snapshot.access_count - neural_pathway_map['temporal_distortion'].get(key, 0)
        spatial_alignment = neural_pathway_map['spatial_alignment'][key]
        
        score = synaptic_strength + temporal_distortion + spatial_alignment
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Synaptic Strength of the accessed entry is incremented, the Temporal Distortion Factor is reset to reflect the current time, and the Spatial Alignment Score is adjusted based on the proximity of the accessed entry to other recent accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    neural_pathway_map['synaptic_strength'][key] += 1
    neural_pathway_map['temporal_distortion'][key] = cache_snapshot.access_count
    
    # Adjust Spatial Alignment Score
    for other_key in cache_snapshot.cache:
        if other_key != key:
            neural_pathway_map['spatial_alignment'][other_key] += SPATIAL_ALIGNMENT_FACTOR

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its Synaptic Strength to a baseline value, sets the Temporal Distortion Factor to the current time, and calculates an initial Spatial Alignment Score based on its position relative to existing entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    neural_pathway_map['synaptic_strength'][key] = BASELINE_SYNAPTIC_STRENGTH
    neural_pathway_map['temporal_distortion'][key] = cache_snapshot.access_count
    
    # Calculate initial Spatial Alignment Score
    for other_key in cache_snapshot.cache:
        if other_key != key:
            neural_pathway_map['spatial_alignment'][other_key] += SPATIAL_ALIGNMENT_FACTOR

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the Neural Pathway Map by removing the evicted entry, adjusts the Synaptic Strength of neighboring entries to reflect the change, and updates the Spatial Alignment Scores to account for the new cache configuration.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del neural_pathway_map['synaptic_strength'][evicted_key]
    del neural_pathway_map['temporal_distortion'][evicted_key]
    del neural_pathway_map['spatial_alignment'][evicted_key]
    
    # Adjust Synaptic Strength and Spatial Alignment Scores
    for key in cache_snapshot.cache:
        neural_pathway_map['synaptic_strength'][key] = max(BASELINE_SYNAPTIC_STRENGTH, neural_pathway_map['synaptic_strength'][key] - 1)
        neural_pathway_map['spatial_alignment'][key] = max(0, neural_pathway_map['spatial_alignment'][key] - SPATIAL_ALIGNMENT_FACTOR)