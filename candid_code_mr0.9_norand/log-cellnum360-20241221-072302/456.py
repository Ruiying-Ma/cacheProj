# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASE_TEMPORAL_SCORE = 1
BASE_CONTEXTUAL_MODULATION = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a cluster map of cache objects based on predictive clustering metrics, temporal access patterns, and contextual signals. Each object is tagged with a cluster ID, a temporal score indicating its recent access frequency, and a contextual modulation factor reflecting its importance in different contexts.
cluster_map = defaultdict(list)  # Maps cluster_id to list of object keys
object_metadata = {}  # Maps object key to (cluster_id, temporal_score, contextual_modulation)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects an eviction victim by identifying the cluster with the lowest combined temporal score and contextual modulation factor. Within this cluster, the object with the lowest temporal score is chosen for eviction, ensuring that less frequently accessed and contextually less important objects are removed first.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_cluster_score = float('inf')
    target_cluster_id = None

    # Find the cluster with the lowest combined score
    for cluster_id, keys in cluster_map.items():
        combined_score = sum(object_metadata[key][1] + object_metadata[key][2] for key in keys)
        if combined_score < min_cluster_score:
            min_cluster_score = combined_score
            target_cluster_id = cluster_id

    # Within the target cluster, find the object with the lowest temporal score
    if target_cluster_id is not None:
        min_temporal_score = float('inf')
        for key in cluster_map[target_cluster_id]:
            temporal_score = object_metadata[key][1]
            if temporal_score < min_temporal_score:
                min_temporal_score = temporal_score
                candid_obj_key = key

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the temporal score of the accessed object is increased, and its contextual modulation factor is adjusted based on the current context. The cluster map is re-evaluated to ensure the object is still in the appropriate cluster based on updated metrics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    if key in object_metadata:
        cluster_id, temporal_score, contextual_modulation = object_metadata[key]
        # Increase temporal score
        temporal_score += 1
        # Adjust contextual modulation factor (this is a placeholder for actual context-based adjustment)
        contextual_modulation += 1
        # Update metadata
        object_metadata[key] = (cluster_id, temporal_score, contextual_modulation)
        # Re-evaluate cluster membership (placeholder logic)
        # For simplicity, assume no change in cluster_id

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns it to a cluster based on initial predictive clustering metrics and sets its temporal score and contextual modulation factor to baseline values. The cluster map is updated to reflect the addition of the new object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    # Assign to a cluster (placeholder logic for initial clustering)
    cluster_id = 0  # Assume a single cluster for simplicity
    temporal_score = BASE_TEMPORAL_SCORE
    contextual_modulation = BASE_CONTEXTUAL_MODULATION
    # Update metadata
    object_metadata[key] = (cluster_id, temporal_score, contextual_modulation)
    cluster_map[cluster_id].append(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the cluster map to account for the removed object, potentially merging or splitting clusters if necessary. It also adjusts the temporal scores and contextual modulation factors of remaining objects in the affected cluster to maintain balance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in object_metadata:
        cluster_id, _, _ = object_metadata.pop(evicted_key)
        cluster_map[cluster_id].remove(evicted_key)
        # Recalibrate cluster (placeholder logic)
        # Adjust temporal scores and contextual modulation factors (placeholder logic)
        # For simplicity, assume no change in cluster structure