# Import anything you need below
from collections import defaultdict
import math

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for Node Entropy Index
BETA = 0.3   # Weight for Predictive Overlay
GAMMA = 0.2  # Weight for Temporal Analytics

# Put the metadata specifically maintained by the policy below. The policy maintains a Node Entropy Index for each cache entry, a Predictive Overlay for access patterns, and a Temporal Analytics log for time-based access frequency. Recursive Integration is used to combine these metrics into a unified score for each entry.
node_entropy_index = defaultdict(float)
predictive_overlay = defaultdict(float)
temporal_analytics = defaultdict(float)

def calculate_unified_score(key):
    # Recursive Integration of the Node Entropy Index, Predictive Overlay, and Temporal Analytics
    return (ALPHA * node_entropy_index[key] +
            BETA * predictive_overlay[key] +
            GAMMA * temporal_analytics[key])

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest unified score, calculated through Recursive Integration of the Node Entropy Index, Predictive Overlay, and Temporal Analytics. This ensures that entries with low access predictability and frequency are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key in cache_snapshot.cache:
        score = calculate_unified_score(key)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Node Entropy Index of the accessed entry is recalculated to reflect increased predictability, the Predictive Overlay is updated to enhance future access predictions, and the Temporal Analytics log is adjusted to reflect the recent access time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    # Recalculate Node Entropy Index
    node_entropy_index[key] = node_entropy_index[key] * 0.9 + 0.1
    # Update Predictive Overlay
    predictive_overlay[key] += 1
    # Update Temporal Analytics
    temporal_analytics[key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Node Entropy Index is initialized based on initial access patterns, the Predictive Overlay is updated to incorporate the new entry's potential access paths, and the Temporal Analytics log is initialized to track future access times.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    # Initialize Node Entropy Index
    node_entropy_index[key] = 0.5
    # Update Predictive Overlay
    predictive_overlay[key] = 0
    # Initialize Temporal Analytics
    temporal_analytics[key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the Node Entropy Index of the evicted entry is removed, the Predictive Overlay is recalibrated to exclude the evicted entry's influence, and the Temporal Analytics log is purged of the evicted entry's data to maintain cache efficiency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    # Remove Node Entropy Index
    if key in node_entropy_index:
        del node_entropy_index[key]
    # Recalibrate Predictive Overlay
    if key in predictive_overlay:
        del predictive_overlay[key]
    # Purge Temporal Analytics
    if key in temporal_analytics:
        del temporal_analytics[key]