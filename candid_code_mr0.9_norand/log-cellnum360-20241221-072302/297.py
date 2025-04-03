# Import anything you need below
from collections import defaultdict, deque

# Put tunable constant parameters below
CONTEXTUAL_MODULATION_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a multi-layered metadata structure: a data flow model capturing access patterns, a granular synthesis map for fine-grained access frequency, a hierarchical reference tree for object relationships, and a contextual modulation score reflecting the current workload context.
data_flow_model = defaultdict(deque)  # Maps object keys to a deque of access paths
granular_synthesis_map = defaultdict(int)  # Maps object keys to their access frequency
hierarchical_reference_tree = defaultdict(set)  # Maps object keys to a set of related object keys
contextual_modulation_score = 1.0  # A score reflecting the current workload context

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects an eviction victim by analyzing the data flow model to identify low-traffic paths, consulting the granular synthesis map for low-frequency objects, and considering the hierarchical reference tree to avoid breaking critical object relationships, all modulated by the current contextual score to adapt to workload changes.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        # Calculate a score for each object based on its frequency and relationships
        frequency = granular_synthesis_map[key]
        relationship_penalty = len(hierarchical_reference_tree[key])
        score = (frequency + relationship_penalty) * contextual_modulation_score
        
        # Find the object with the lowest score
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the data flow model is updated to reinforce the accessed path, the granular synthesis map increments the frequency of the accessed object, the hierarchical reference tree strengthens the link of the accessed object, and the contextual modulation score is adjusted to reflect the current workload dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Reinforce the accessed path in the data flow model
    data_flow_model[obj.key].append(cache_snapshot.access_count)
    
    # Increment the frequency of the accessed object
    granular_synthesis_map[obj.key] += 1
    
    # Strengthen the link of the accessed object in the hierarchical reference tree
    # Assuming some logic to determine related objects, here we just reinforce existing links
    for related_key in hierarchical_reference_tree[obj.key]:
        hierarchical_reference_tree[related_key].add(obj.key)
    
    # Adjust the contextual modulation score
    global contextual_modulation_score
    contextual_modulation_score += CONTEXTUAL_MODULATION_FACTOR

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the data flow model incorporates the new object into its access paths, the granular synthesis map initializes its frequency, the hierarchical reference tree updates to include the new object in its structure, and the contextual modulation score is recalibrated to account for the new addition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Incorporate the new object into the data flow model
    data_flow_model[obj.key] = deque([cache_snapshot.access_count])
    
    # Initialize its frequency in the granular synthesis map
    granular_synthesis_map[obj.key] = 1
    
    # Update the hierarchical reference tree to include the new object
    hierarchical_reference_tree[obj.key] = set()
    
    # Recalibrate the contextual modulation score
    global contextual_modulation_score
    contextual_modulation_score -= CONTEXTUAL_MODULATION_FACTOR

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the data flow model removes or weakens paths involving the evicted object, the granular synthesis map resets its frequency, the hierarchical reference tree prunes the evicted object, and the contextual modulation score is adjusted to reflect the change in cache composition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Remove or weaken paths involving the evicted object in the data flow model
    if evicted_obj.key in data_flow_model:
        del data_flow_model[evicted_obj.key]
    
    # Reset its frequency in the granular synthesis map
    if evicted_obj.key in granular_synthesis_map:
        del granular_synthesis_map[evicted_obj.key]
    
    # Prune the evicted object from the hierarchical reference tree
    if evicted_obj.key in hierarchical_reference_tree:
        del hierarchical_reference_tree[evicted_obj.key]
    
    # Adjust the contextual modulation score
    global contextual_modulation_score
    contextual_modulation_score += CONTEXTUAL_MODULATION_FACTOR