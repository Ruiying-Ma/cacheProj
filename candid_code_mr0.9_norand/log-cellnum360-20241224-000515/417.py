# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
TEMPORAL_WEIGHT = 0.25
LOAD_WEIGHT = 0.25
PREDICTIVE_WEIGHT = 0.25
CONTEXTUAL_WEIGHT = 0.25

# Put the metadata specifically maintained by the policy below. The policy maintains a temporal index for each cache entry, a load score indicating the resource usage of each entry, a predictive score based on access patterns, and a contextual map linking entries to specific usage contexts.
temporal_index = {}
load_score = {}
predictive_score = {}
contextual_map = defaultdict(set)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each entry, which is a weighted sum of the temporal index, load score, predictive score, and contextual relevance. The entry with the lowest composite score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        composite_score = (
            TEMPORAL_WEIGHT * temporal_index.get(key, 0) +
            LOAD_WEIGHT * load_score.get(key, 0) +
            PREDICTIVE_WEIGHT * predictive_score.get(key, 0) +
            CONTEXTUAL_WEIGHT * len(contextual_map[key])
        )
        
        if composite_score < min_score:
            min_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the temporal index is updated to reflect the current time, the load score is adjusted based on recent resource usage, the predictive score is recalibrated using recent access patterns, and the contextual map is refined to better associate the entry with its usage context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    temporal_index[key] = cache_snapshot.access_count
    load_score[key] = obj.size
    predictive_score[key] += 1
    contextual_map[key].add('hit_context')

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the temporal index is initialized to the current time, the load score is set based on the initial resource usage estimate, the predictive score is initialized using historical access data, and the contextual map is updated to include the new entry's context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    temporal_index[key] = cache_snapshot.access_count
    load_score[key] = obj.size
    predictive_score[key] = 1
    contextual_map[key].add('insert_context')

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the temporal index is recalibrated to prioritize remaining entries, the load score is redistributed to reflect the reduced cache load, the predictive score is adjusted to account for the change in access patterns, and the contextual map is updated to remove the evicted entry's context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in temporal_index:
        del temporal_index[evicted_key]
    if evicted_key in load_score:
        del load_score[evicted_key]
    if evicted_key in predictive_score:
        del predictive_score[evicted_key]
    if evicted_key in contextual_map:
        del contextual_map[evicted_key]
    
    # Recalibrate remaining entries
    for key in cache_snapshot.cache:
        temporal_index[key] = cache_snapshot.access_count
        load_score[key] = cache_snapshot.cache[key].size
        predictive_score[key] = max(1, predictive_score[key] - 1)