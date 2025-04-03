# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_ACCESS_FREQUENCY = 1
INITIAL_RECENCY_SCORE = 1
INITIAL_VIRTUAL_RESOURCE_SCORE = 1.0
PREDICTIVE_LOAD_BALANCING_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a dynamic hierarchy of cache blocks based on access frequency and recency, virtual resource allocation scores for each block, predictive load balancing metrics, and synchronized efficiency indicators for cache performance.
access_frequency = defaultdict(int)
recency_score = defaultdict(int)
virtual_resource_score = defaultdict(float)
predictive_load_balancing = defaultdict(float)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the cache block with the lowest combined score of virtual resource allocation and predictive load balancing, while ensuring synchronized efficiency is maintained across the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_combined_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = virtual_resource_score[key] + predictive_load_balancing[key]
        if combined_score < min_combined_score:
            min_combined_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the access frequency and recency score of the accessed block, adjusts its virtual resource allocation score upwards, and recalibrates predictive load balancing metrics to reflect the current access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] += 1
    recency_score[key] = cache_snapshot.access_count
    virtual_resource_score[key] += 1.0
    predictive_load_balancing[key] += PREDICTIVE_LOAD_BALANCING_FACTOR

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns initial scores for access frequency and recency, sets a baseline virtual resource allocation score, and updates predictive load balancing metrics to account for the new addition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] = INITIAL_ACCESS_FREQUENCY
    recency_score[key] = cache_snapshot.access_count
    virtual_resource_score[key] = INITIAL_VIRTUAL_RESOURCE_SCORE
    predictive_load_balancing[key] = PREDICTIVE_LOAD_BALANCING_FACTOR

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the dynamic hierarchy to reflect the removal, adjusts virtual resource allocation scores for remaining blocks, and updates predictive load balancing metrics to ensure synchronized efficiency is maintained.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del access_frequency[evicted_key]
    del recency_score[evicted_key]
    del virtual_resource_score[evicted_key]
    del predictive_load_balancing[evicted_key]
    
    for key in cache_snapshot.cache:
        virtual_resource_score[key] *= 0.9
        predictive_load_balancing[key] *= 0.9