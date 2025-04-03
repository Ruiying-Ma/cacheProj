# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_COGNITIVE_INDEX = 1.0
NEUTRAL_REFLEXIVE_INDEX = 1.0
COGNITIVE_INCREMENT = 0.1
REFLEXIVE_ADJUSTMENT_FACTOR = 0.05

# Put the metadata specifically maintained by the policy below. The policy maintains a cognitive index for each cache entry, which includes access frequency, recency, and a synthesized data score derived from the relationship between accessed data patterns. It also keeps a reflexive index that dynamically adjusts based on the cache's overall performance and workload characteristics.
cognitive_index = defaultdict(lambda: INITIAL_COGNITIVE_INDEX)
reflexive_index = defaultdict(lambda: NEUTRAL_REFLEXIVE_INDEX)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest cognitive index score, factoring in both the synthesized data score and reflexive index. This ensures that the least contextually valuable and adaptable entry is removed.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = cognitive_index[key] * reflexive_index[key]
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the cognitive index of the accessed entry is incremented to reflect increased access frequency and recency. The reflexive index is adjusted to optimize for current workload patterns, enhancing the entry's adaptability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    cognitive_index[obj.key] += COGNITIVE_INCREMENT
    reflexive_index[obj.key] += REFLEXIVE_ADJUSTMENT_FACTOR

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its cognitive index based on initial access patterns and assigns a neutral reflexive index. This allows the entry to quickly adapt to its relevance within the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    cognitive_index[obj.key] = INITIAL_COGNITIVE_INDEX
    reflexive_index[obj.key] = NEUTRAL_REFLEXIVE_INDEX

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the reflexive index across all remaining entries to ensure optimal performance under the current workload, while also adjusting the cognitive index of similar entries to prevent future unnecessary evictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        reflexive_index[key] *= (1 - REFLEXIVE_ADJUSTMENT_FACTOR)
        if key != evicted_obj.key:
            cognitive_index[key] *= (1 + COGNITIVE_INCREMENT / 2)