# Import anything you need below
from collections import defaultdict
import math

# Put tunable constant parameters below
TEMPORAL_DECAY_FACTOR = 0.1  # Decay factor for temporal relevance

# Put the metadata specifically maintained by the policy below. The policy maintains a Quantum Topology Map (QTM) that represents cache entries as nodes in a quantum graph, with edges weighted by access frequency and recency. Each node also holds a Recursive Integration Score (RIS) that aggregates past access patterns, and an Entropic Displacement Value (EDV) that measures the unpredictability of access sequences. A Temporal Framework (TF) is used to timestamp each access and insertion event.
QTM = defaultdict(lambda: {'edges': defaultdict(int), 'RIS': 0, 'EDV': 0, 'timestamp': 0})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the node with the lowest combined score of RIS and EDV, adjusted by the temporal decay factor from the TF. This approach prioritizes evicting entries that are both infrequently accessed and have unpredictable access patterns, while considering their temporal relevance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, node in QTM.items():
        age = cache_snapshot.access_count - node['timestamp']
        temporal_decay = math.exp(-TEMPORAL_DECAY_FACTOR * age)
        score = (node['RIS'] + node['EDV']) * temporal_decay
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the QTM is updated by increasing the weight of edges connected to the accessed node, reflecting increased access frequency. The RIS of the node is recalculated to integrate the new access pattern, and the EDV is adjusted to reflect any changes in access predictability. The TF is updated with the current timestamp for the accessed node.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    node = QTM[obj.key]
    node['timestamp'] = cache_snapshot.access_count
    
    # Increase edge weights
    for other_key in cache_snapshot.cache:
        if other_key != obj.key:
            node['edges'][other_key] += 1
    
    # Recalculate RIS and EDV
    node['RIS'] = sum(node['edges'].values())
    node['EDV'] = 1 / (1 + node['RIS'])  # Simplified unpredictability measure

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the QTM adds a new node with initial edge weights based on predicted access patterns. The RIS is initialized using a baseline integration of expected access frequency, and the EDV is set to a neutral value indicating unknown predictability. The TF records the insertion time for the new node.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    QTM[obj.key] = {
        'edges': defaultdict(int),
        'RIS': 1,  # Baseline RIS
        'EDV': 0.5,  # Neutral EDV
        'timestamp': cache_snapshot.access_count
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the QTM removes the node and its associated edges, recalibrating the topology to reflect the change. The RIS and EDV of remaining nodes are adjusted to account for the altered access landscape. The TF is updated to remove the timestamp of the evicted node, ensuring temporal accuracy for future operations.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Remove the evicted node
    if evicted_obj.key in QTM:
        del QTM[evicted_obj.key]
    
    # Recalibrate the topology
    for node in QTM.values():
        if evicted_obj.key in node['edges']:
            del node['edges'][evicted_obj.key]
        
        # Recalculate RIS and EDV
        node['RIS'] = sum(node['edges'].values())
        node['EDV'] = 1 / (1 + node['RIS'])  # Simplified unpredictability measure