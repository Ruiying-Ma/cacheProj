# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.4
PERSISTENCE_WEIGHT = 0.3
CLUSTERING_WEIGHT = 0.3

# Put the metadata specifically maintained by the policy below. The policy maintains a frequency distribution of access counts for each cache item, a persistence score indicating how long an item has been in the cache, a clustering score that groups accesses based on temporal proximity, and a load normalization factor that adjusts scores based on current cache load.
frequency_count = defaultdict(int)
persistence_score = defaultdict(int)
clustering_score = defaultdict(float)
load_normalization_factor = 1.0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each item, which is a weighted sum of its frequency distribution, persistence score, and clustering score, normalized by the load factor. The item with the lowest composite score is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        freq = frequency_count[key]
        persist = persistence_score[key]
        cluster = clustering_score[key]
        
        composite_score = (
            (FREQUENCY_WEIGHT * freq + 
             PERSISTENCE_WEIGHT * persist + 
             CLUSTERING_WEIGHT * cluster) / load_normalization_factor
        )
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the frequency count for the accessed item is incremented, its clustering score is adjusted to reflect recent access, and the load normalization factor is recalculated to account for the current cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    frequency_count[key] += 1
    clustering_score[key] = cache_snapshot.access_count
    load_normalization_factor = cache_snapshot.size / cache_snapshot.capacity

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its frequency count to 1, sets its persistence score to a baseline value, assigns a clustering score based on recent access patterns, and updates the load normalization factor to reflect the increased cache load.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    frequency_count[key] = 1
    persistence_score[key] = cache_snapshot.access_count
    clustering_score[key] = cache_snapshot.access_count
    load_normalization_factor = cache_snapshot.size / cache_snapshot.capacity

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the metadata of the evicted item, recalculates the persistence scores for remaining items to reflect their relative longevity, and updates the load normalization factor to account for the reduced cache load.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del frequency_count[evicted_key]
    del persistence_score[evicted_key]
    del clustering_score[evicted_key]
    
    for key in persistence_score:
        persistence_score[key] = cache_snapshot.access_count - persistence_score[key]
    
    load_normalization_factor = cache_snapshot.size / cache_snapshot.capacity