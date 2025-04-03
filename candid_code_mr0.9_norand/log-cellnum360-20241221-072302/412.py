# Import anything you need below
import numpy as np
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_FIDELITY_SCORE = 1.0
FIDELITY_DECAY = 0.9
CONGRUENCE_STRENGTHEN_FACTOR = 1.1

# Put the metadata specifically maintained by the policy below. The policy maintains a Semantic Congruence Matrix to track the relationship between cached items, a Temporal Synthesis Node to record access patterns over time, and a Data Fidelity Assurance score to ensure the integrity and relevance of cached data.
semantic_congruence_matrix = defaultdict(lambda: defaultdict(float))
temporal_synthesis_node = {}
data_fidelity_scores = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by analyzing the Semantic Congruence Matrix to find items with the least semantic relevance to current access patterns, as well as considering the Temporal Synthesis Node to identify items with outdated access patterns, while ensuring Data Fidelity Assurance is maintained.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        # Calculate a score based on semantic congruence, temporal synthesis, and data fidelity
        congruence_score = sum(semantic_congruence_matrix[key].values())
        time_since_last_access = cache_snapshot.access_count - temporal_synthesis_node[key]
        fidelity_score = data_fidelity_scores[key]
        
        # Combine these factors to determine the eviction score
        eviction_score = (congruence_score * time_since_last_access) / fidelity_score
        
        if eviction_score < min_score:
            min_score = eviction_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Temporal Synthesis Node is updated to reflect the latest access time, the Semantic Congruence Matrix is adjusted to strengthen the relationship of the accessed item with others, and the Data Fidelity Assurance score is recalibrated to ensure continued relevance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Update Temporal Synthesis Node
    temporal_synthesis_node[obj.key] = cache_snapshot.access_count
    
    # Strengthen Semantic Congruence Matrix
    for other_key in cache_snapshot.cache:
        if other_key != obj.key:
            semantic_congruence_matrix[obj.key][other_key] *= CONGRUENCE_STRENGTHEN_FACTOR
            semantic_congruence_matrix[other_key][obj.key] *= CONGRUENCE_STRENGTHEN_FACTOR
    
    # Recalibrate Data Fidelity Assurance score
    data_fidelity_scores[obj.key] *= FIDELITY_DECAY

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Semantic Congruence Matrix is expanded to include the new item, the Temporal Synthesis Node is initialized with the current time for the new item, and the Data Fidelity Assurance score is set to a baseline value to start tracking its relevance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Initialize Temporal Synthesis Node
    temporal_synthesis_node[obj.key] = cache_snapshot.access_count
    
    # Expand Semantic Congruence Matrix
    for other_key in cache_snapshot.cache:
        semantic_congruence_matrix[obj.key][other_key] = 1.0
        semantic_congruence_matrix[other_key][obj.key] = 1.0
    
    # Set Data Fidelity Assurance score
    data_fidelity_scores[obj.key] = BASELINE_FIDELITY_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the Semantic Congruence Matrix is pruned to remove the evicted item, the Temporal Synthesis Node is updated to remove its access history, and the Data Fidelity Assurance score is recalculated to reflect the current cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Prune Semantic Congruence Matrix
    if evicted_obj.key in semantic_congruence_matrix:
        del semantic_congruence_matrix[evicted_obj.key]
    for other_key in semantic_congruence_matrix:
        if evicted_obj.key in semantic_congruence_matrix[other_key]:
            del semantic_congruence_matrix[other_key][evicted_obj.key]
    
    # Remove from Temporal Synthesis Node
    if evicted_obj.key in temporal_synthesis_node:
        del temporal_synthesis_node[evicted_obj.key]
    
    # Recalculate Data Fidelity Assurance score
    if evicted_obj.key in data_fidelity_scores:
        del data_fidelity_scores[evicted_obj.key]