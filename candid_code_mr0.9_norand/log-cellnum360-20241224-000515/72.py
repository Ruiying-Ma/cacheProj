# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
CONSISTENCY_WEIGHT = 1.0
PARALLEL_ACCESS_WEIGHT = 1.0
QUEUE_POSITION_WEIGHT = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a metadata structure that includes a consistency score for each cache entry, a parallel access counter, a queue position index, and an optimization weight. The consistency score reflects the likelihood of data being stale, the parallel access counter tracks concurrent accesses, the queue position index helps in balancing, and the optimization weight is used for algorithmic prioritization.
metadata = defaultdict(lambda: {
    'consistency_score': 1.0,
    'parallel_access_counter': 0,
    'queue_position_index': 0,
    'optimization_weight': 1.0
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache entry, which is a weighted sum of the inverse of the consistency score, the parallel access counter, and the queue position index. The entry with the lowest composite score is selected for eviction, ensuring that less consistent, less accessed, and poorly balanced entries are prioritized for removal.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        composite_score = (
            CONSISTENCY_WEIGHT / meta['consistency_score'] +
            PARALLEL_ACCESS_WEIGHT * meta['parallel_access_counter'] +
            QUEUE_POSITION_WEIGHT * meta['queue_position_index']
        )
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the parallel access counter for the accessed entry, recalculates its consistency score based on recent data access patterns, and adjusts its queue position index to reflect its increased priority. The optimization weight is updated to reflect the entry's improved relevance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['parallel_access_counter'] += 1
    meta['consistency_score'] = 1.0 / (1 + meta['parallel_access_counter'])
    meta['queue_position_index'] = 0  # Move to the front of the queue
    meta['optimization_weight'] += 0.1  # Increase relevance

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its consistency score based on initial data freshness, sets the parallel access counter to zero, assigns a queue position index based on current queue balance, and calculates an initial optimization weight to integrate it smoothly into the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['consistency_score'] = 1.0  # Fresh data
    meta['parallel_access_counter'] = 0
    meta['queue_position_index'] = len(cache_snapshot.cache)  # End of the queue
    meta['optimization_weight'] = 1.0  # Initial weight

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy rebalances the queue position indices of remaining entries to maintain optimal queue balance, adjusts the optimization weights of neighboring entries to reflect the change in cache composition, and recalibrates the consistency scores of affected entries to ensure ongoing data integrity.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    del metadata[evicted_obj.key]
    
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        meta['queue_position_index'] -= 1  # Rebalance queue positions
        meta['optimization_weight'] *= 0.9  # Adjust weights
        meta['consistency_score'] = 1.0 / (1 + meta['parallel_access_counter'])  # Recalibrate consistency