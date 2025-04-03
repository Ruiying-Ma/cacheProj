# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
COHERENCE_WEIGHT = 0.25
PRIORITY_WEIGHT = 0.25
PREDICTIVE_WEIGHT = 0.25
FORESIGHT_WEIGHT = 0.25

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a coherence score for each cache entry, a dynamic task priority level, a predictive adjustment factor, and a strategic foresight index. The coherence score reflects the likelihood of data being accessed together, the task priority level indicates the importance of the data for ongoing tasks, the predictive adjustment factor anticipates future access patterns, and the strategic foresight index evaluates long-term utility.
metadata = defaultdict(lambda: {
    'coherence_score': 0,
    'task_priority_level': 0,
    'predictive_adjustment_factor': 0,
    'strategic_foresight_index': 0
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache entry, which is a weighted sum of the coherence score, task priority level, predictive adjustment factor, and strategic foresight index. The entry with the lowest composite score is selected for eviction, ensuring that the least strategically valuable data is removed.
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
            COHERENCE_WEIGHT * meta['coherence_score'] +
            PRIORITY_WEIGHT * meta['task_priority_level'] +
            PREDICTIVE_WEIGHT * meta['predictive_adjustment_factor'] +
            FORESIGHT_WEIGHT * meta['strategic_foresight_index']
        )
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the coherence score of the accessed entry is increased, reflecting its relevance. The task priority level is adjusted based on current task demands, the predictive adjustment factor is recalibrated using recent access patterns, and the strategic foresight index is updated to reflect the entry's continued utility.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['coherence_score'] += 1
    meta['task_priority_level'] += 1
    meta['predictive_adjustment_factor'] += 1
    meta['strategic_foresight_index'] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the coherence score is initialized based on initial access patterns, the task priority level is set according to the current task context, the predictive adjustment factor is estimated using historical data, and the strategic foresight index is calculated to project potential long-term value.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['coherence_score'] = 1
    meta['task_priority_level'] = 1
    meta['predictive_adjustment_factor'] = 1
    meta['strategic_foresight_index'] = 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the coherence scores of remaining entries to reflect the new cache state, adjusts task priority levels to redistribute focus, updates predictive adjustment factors to account for the change in cache composition, and revises strategic foresight indices to ensure alignment with future access trends.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        meta = metadata[key]
        meta['coherence_score'] = max(0, meta['coherence_score'] - 1)
        meta['task_priority_level'] = max(0, meta['task_priority_level'] - 1)
        meta['predictive_adjustment_factor'] = max(0, meta['predictive_adjustment_factor'] - 1)
        meta['strategic_foresight_index'] = max(0, meta['strategic_foresight_index'] - 1)