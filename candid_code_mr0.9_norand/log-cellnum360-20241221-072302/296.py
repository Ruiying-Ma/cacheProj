# Import anything you need below
from collections import defaultdict, deque

# Put tunable constant parameters below
INITIAL_CONSENSUS_SCORE = 1
INITIAL_QUORUM_THRESHOLD = 5
HIGH_NETWORK_SYNCHRONY_THRESHOLD = 10

# Put the metadata specifically maintained by the policy below. The policy maintains a hierarchical cluster of cache objects, where each cluster represents a group of objects with similar access patterns. Each cluster has a consensus score indicating the agreement level among nodes about the importance of the objects within it. Additionally, an adaptive quorum threshold is maintained to dynamically adjust the required consensus for eviction decisions based on network synchrony.
clusters = defaultdict(lambda: {'objects': deque(), 'consensus_score': INITIAL_CONSENSUS_SCORE})
adaptive_quorum_threshold = INITIAL_QUORUM_THRESHOLD

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the cluster with the lowest consensus score and selecting the least recently used object within that cluster. If network synchrony is high, the adaptive quorum threshold is lowered, allowing for quicker eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    # Find the cluster with the lowest consensus score
    min_consensus_score = float('inf')
    target_cluster = None
    for cluster_id, cluster_data in clusters.items():
        if cluster_data['consensus_score'] < min_consensus_score:
            min_consensus_score = cluster_data['consensus_score']
            target_cluster = cluster_data

    # Select the least recently used object within that cluster
    if target_cluster and target_cluster['objects']:
        candid_obj_key = target_cluster['objects'].popleft().key

    # Adjust quorum threshold based on network synchrony
    if cache_snapshot.access_count - cache_snapshot.hit_count < HIGH_NETWORK_SYNCHRONY_THRESHOLD:
        global adaptive_quorum_threshold
        adaptive_quorum_threshold = max(1, adaptive_quorum_threshold - 1)

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the consensus score of the cluster containing the accessed object is incremented, reflecting increased importance. The object's position within the cluster is updated to reflect recent access, and the adaptive quorum threshold is adjusted based on current network synchrony.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    for cluster_id, cluster_data in clusters.items():
        if obj in cluster_data['objects']:
            # Increment consensus score
            cluster_data['consensus_score'] += 1
            # Update object's position to reflect recent access
            cluster_data['objects'].remove(obj)
            cluster_data['objects'].append(obj)
            break

    # Adjust quorum threshold based on network synchrony
    if cache_snapshot.access_count - cache_snapshot.hit_count < HIGH_NETWORK_SYNCHRONY_THRESHOLD:
        global adaptive_quorum_threshold
        adaptive_quorum_threshold = max(1, adaptive_quorum_threshold - 1)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns it to the most appropriate cluster based on its access pattern. The consensus score of the cluster is recalculated to include the new object, and the adaptive quorum threshold is adjusted to reflect the current network conditions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    # Assign the object to a cluster (for simplicity, we use a single cluster)
    cluster_id = 0  # Simplified: all objects go to the same cluster
    clusters[cluster_id]['objects'].append(obj)
    # Recalculate consensus score
    clusters[cluster_id]['consensus_score'] += 1

    # Adjust quorum threshold based on network synchrony
    if cache_snapshot.access_count - cache_snapshot.hit_count < HIGH_NETWORK_SYNCHRONY_THRESHOLD:
        global adaptive_quorum_threshold
        adaptive_quorum_threshold = max(1, adaptive_quorum_threshold - 1)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the consensus score of the affected cluster is decremented, and the cluster hierarchy is re-evaluated to ensure optimal grouping. The adaptive quorum threshold is recalibrated to maintain balance between eviction speed and decision accuracy, considering network synchrony.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    for cluster_id, cluster_data in clusters.items():
        if evicted_obj in cluster_data['objects']:
            # Decrement consensus score
            cluster_data['consensus_score'] -= 1
            # Remove evicted object
            cluster_data['objects'].remove(evicted_obj)
            break

    # Re-evaluate cluster hierarchy (simplified: no actual re-evaluation logic)
    # Recalibrate quorum threshold
    if cache_snapshot.access_count - cache_snapshot.hit_count < HIGH_NETWORK_SYNCHRONY_THRESHOLD:
        global adaptive_quorum_threshold
        adaptive_quorum_threshold = max(1, adaptive_quorum_threshold - 1)