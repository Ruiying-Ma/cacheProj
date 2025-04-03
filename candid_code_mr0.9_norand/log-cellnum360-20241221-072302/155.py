# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
PREDICTIVE_CLUSTER_WEIGHT = 0.25
LOAD_SYNC_WEIGHT = 0.25
DATA_PROPAGATION_WEIGHT = 0.25
CONTEXTUAL_INDEX_WEIGHT = 0.25

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive cluster map of data access patterns, a load synchronization index to track cache load balance, a data propagation score to assess the importance of data sharing across nodes, and a contextual index to capture the context in which data is accessed.
predictive_cluster_map = defaultdict(float)
load_sync_index = defaultdict(float)
data_propagation_score = defaultdict(float)
contextual_index = defaultdict(float)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the data with the lowest combined score of predictive cluster relevance, load synchronization necessity, data propagation importance, and contextual access frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (PREDICTIVE_CLUSTER_WEIGHT * predictive_cluster_map[key] +
                 LOAD_SYNC_WEIGHT * load_sync_index[key] +
                 DATA_PROPAGATION_WEIGHT * data_propagation_score[key] +
                 CONTEXTUAL_INDEX_WEIGHT * contextual_index[key])
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive cluster map is refined to enhance future access predictions, the load synchronization index is adjusted to reflect the current load balance, the data propagation score is incremented to indicate increased sharing potential, and the contextual index is updated to capture the current access context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    predictive_cluster_map[obj.key] += 1.0
    load_sync_index[obj.key] = cache_snapshot.size / cache_snapshot.capacity
    data_propagation_score[obj.key] += 1.0
    contextual_index[obj.key] += 1.0

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the predictive cluster map is updated to include the new access pattern, the load synchronization index is recalibrated to account for the new load, the data propagation score is initialized based on initial sharing potential, and the contextual index is set to reflect the initial access context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    predictive_cluster_map[obj.key] = 1.0
    load_sync_index[obj.key] = cache_snapshot.size / cache_snapshot.capacity
    data_propagation_score[obj.key] = 1.0
    contextual_index[obj.key] = 1.0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the predictive cluster map is adjusted to remove outdated patterns, the load synchronization index is recalibrated to reflect the reduced load, the data propagation score is decremented to indicate reduced sharing potential, and the contextual index is updated to remove the evicted context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    if evicted_obj.key in predictive_cluster_map:
        del predictive_cluster_map[evicted_obj.key]
    if evicted_obj.key in load_sync_index:
        del load_sync_index[evicted_obj.key]
    if evicted_obj.key in data_propagation_score:
        del data_propagation_score[evicted_obj.key]
    if evicted_obj.key in contextual_index:
        del contextual_index[evicted_obj.key]