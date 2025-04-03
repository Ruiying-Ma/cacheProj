# Import anything you need below
from collections import defaultdict, deque

# Put tunable constant parameters below
SYNTHESIS_SCORE_INCREMENT = 1
ACCESS_FREQUENCY_THRESHOLD = 5

# Put the metadata specifically maintained by the policy below. The policy maintains a hierarchical structure of cache blocks, where each block is associated with temporal access patterns and synthesis scores. It also tracks adaptive restructuring metrics to dynamically adjust the hierarchy based on access frequency and recency.
class CacheMetadata:
    def __init__(self):
        self.hierarchy = defaultdict(deque)  # Hierarchy levels with deque for each level
        self.synthesis_scores = defaultdict(int)  # Synthesis scores for each object
        self.access_frequencies = defaultdict(int)  # Access frequencies for each object
        self.temporal_patterns = defaultdict(int)  # Temporal patterns for each object

cache_metadata = CacheMetadata()

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects an eviction victim by evaluating the lowest synthesis score within the least frequently accessed hierarchy level, while also considering temporal patterns to avoid evicting blocks that may soon be reused.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_level = min(cache_metadata.hierarchy.keys(), default=None)
    if min_level is not None:
        min_score = float('inf')
        for key in cache_metadata.hierarchy[min_level]:
            if cache_metadata.synthesis_scores[key] < min_score:
                min_score = cache_metadata.synthesis_scores[key]
                candid_obj_key = key
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the synthesis score of the accessed block, updates its temporal access pattern, and may promote it to a higher hierarchy level if its access frequency surpasses a threshold.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    cache_metadata.synthesis_scores[obj.key] += SYNTHESIS_SCORE_INCREMENT
    cache_metadata.access_frequencies[obj.key] += 1
    cache_metadata.temporal_patterns[obj.key] = cache_snapshot.access_count

    current_level = None
    for level, keys in cache_metadata.hierarchy.items():
        if obj.key in keys:
            current_level = level
            break

    if current_level is not None and cache_metadata.access_frequencies[obj.key] > ACCESS_FREQUENCY_THRESHOLD:
        cache_metadata.hierarchy[current_level].remove(obj.key)
        cache_metadata.hierarchy[current_level + 1].append(obj.key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its synthesis score and temporal pattern, placing it in the appropriate hierarchy level based on initial access predictions. It also recalibrates the adaptive restructuring metrics to accommodate the new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    cache_metadata.synthesis_scores[obj.key] = 0
    cache_metadata.access_frequencies[obj.key] = 0
    cache_metadata.temporal_patterns[obj.key] = cache_snapshot.access_count
    cache_metadata.hierarchy[0].append(obj.key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalculates synthesis scores for remaining blocks in the affected hierarchy level, adjusts temporal patterns to reflect the change, and updates adaptive restructuring metrics to optimize future cache organization.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    for level, keys in cache_metadata.hierarchy.items():
        if evicted_obj.key in keys:
            keys.remove(evicted_obj.key)
            break

    # Recalculate synthesis scores and adjust temporal patterns
    for key in cache_snapshot.cache:
        cache_metadata.synthesis_scores[key] = max(0, cache_metadata.synthesis_scores[key] - 1)
        cache_metadata.temporal_patterns[key] = cache_snapshot.access_count