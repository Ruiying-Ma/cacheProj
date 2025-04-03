# Import anything you need below
from collections import defaultdict
import heapq

# Put tunable constant parameters below
INITIAL_PRIORITY = 1.0
LATENCY_WEIGHT = 0.5
FREQUENCY_WEIGHT = 0.5
ADAPTIVE_BUFFER_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including an optimized index for quick access, a priority score for each cache entry, estimated latency for accessing each entry, and an adaptive buffer size that adjusts based on access patterns.
priority_scores = defaultdict(lambda: INITIAL_PRIORITY)
access_frequencies = defaultdict(int)
estimated_latencies = defaultdict(lambda: 1.0)
optimized_index = []
adaptive_buffer_size = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest priority score, factoring in both the estimated latency and the frequency of access, while ensuring the adaptive buffer is not exceeded.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    while optimized_index:
        priority, key = heapq.heappop(optimized_index)
        if key in cache_snapshot.cache:
            candid_obj_key = key
            break
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the priority score of the accessed entry is increased, the estimated latency is recalibrated based on the current access time, and the entry's position in the optimized index is adjusted to reflect its new priority.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    access_frequencies[key] += 1
    estimated_latencies[key] = (estimated_latencies[key] + (cache_snapshot.access_count - estimated_latencies[key])) / 2
    priority_scores[key] = LATENCY_WEIGHT * estimated_latencies[key] + FREQUENCY_WEIGHT * access_frequencies[key]
    heapq.heappush(optimized_index, (priority_scores[key], key))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial priority score based on estimated latency and expected access frequency, updates the optimized index to include the new entry, and recalibrates the adaptive buffer size if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    access_frequencies[key] = 1
    estimated_latencies[key] = cache_snapshot.access_count
    priority_scores[key] = LATENCY_WEIGHT * estimated_latencies[key] + FREQUENCY_WEIGHT * access_frequencies[key]
    heapq.heappush(optimized_index, (priority_scores[key], key))
    adaptive_buffer_size = int(ADAPTIVE_BUFFER_FACTOR * cache_snapshot.capacity)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the entry from the optimized index, recalculates the priority scores of remaining entries to ensure balance, and adjusts the adaptive buffer size to optimize future cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in priority_scores:
        del priority_scores[evicted_key]
        del access_frequencies[evicted_key]
        del estimated_latencies[evicted_key]
    # Recalculate priority scores for balance
    for key in cache_snapshot.cache:
        priority_scores[key] = LATENCY_WEIGHT * estimated_latencies[key] + FREQUENCY_WEIGHT * access_frequencies[key]
        heapq.heappush(optimized_index, (priority_scores[key], key))
    adaptive_buffer_size = int(ADAPTIVE_BUFFER_FACTOR * cache_snapshot.capacity)