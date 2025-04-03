# Import anything you need below
from collections import defaultdict
import heapq

# Put tunable constant parameters below
DEFAULT_EVENT_PRIORITY = 1
CONTEXT_SWITCH_PENALTY = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a serialized data structure for each cache entry that records access frequency, last access time, and event priority. It also tracks context switches between different execution pipelines to understand the workload dynamics.
cache_metadata = {
    'access_frequency': defaultdict(int),
    'last_access_time': {},
    'event_priority': defaultdict(lambda: DEFAULT_EVENT_PRIORITY),
    'context_switch_count': defaultdict(int)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by prioritizing entries with the lowest event priority and least recent access time. It also considers the context switch frequency, preferring to evict entries that are less relevant to the current execution pipeline.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_priority = float('inf')
    min_time = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        priority = cache_metadata['event_priority'][key]
        last_access = cache_metadata['last_access_time'].get(key, 0)
        context_switch = cache_metadata['context_switch_count'][key]
        
        # Calculate effective priority considering context switch
        effective_priority = priority + context_switch * CONTEXT_SWITCH_PENALTY
        
        if effective_priority < min_priority or (effective_priority == min_priority and last_access < min_time):
            min_priority = effective_priority
            min_time = last_access
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency and last access time in the serialized data structure. It also adjusts the event priority based on the current execution pipeline context to ensure relevance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    cache_metadata['access_frequency'][key] += 1
    cache_metadata['last_access_time'][key] = cache_snapshot.access_count
    # Adjust event priority based on some context (not specified, so using a simple increment)
    cache_metadata['event_priority'][key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its metadata with a default event priority and sets the access frequency and last access time. It also logs the context switch to align the entry with the current execution pipeline.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    cache_metadata['access_frequency'][key] = 1
    cache_metadata['last_access_time'][key] = cache_snapshot.access_count
    cache_metadata['event_priority'][key] = DEFAULT_EVENT_PRIORITY
    # Log context switch (not specified, so using a simple increment)
    cache_metadata['context_switch_count'][key] += 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the event priority thresholds and context switch metrics to better align future eviction decisions with the observed workload patterns and execution pipeline dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    # Recalibrate event priority thresholds (not specified, so using a simple decrement)
    cache_metadata['event_priority'][evicted_key] = max(0, cache_metadata['event_priority'][evicted_key] - 1)
    # Reset context switch count for evicted object
    cache_metadata['context_switch_count'][evicted_key] = 0