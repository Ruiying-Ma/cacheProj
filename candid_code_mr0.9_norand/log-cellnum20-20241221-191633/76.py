# Import anything you need below
from collections import defaultdict
import time

# Put tunable constant parameters below
BASELINE_FREQUENCY = 1
DEFAULT_PRIORITY = 1
LOAD_STATUS_FACTOR = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, priority levels, load status, and a real-time frequency update counter for each cache entry. Access frequency is adjusted using adaptive frequency scaling, while priority levels help manage priority inversion. Load status reflects the current system load, and the frequency update counter tracks real-time changes.
metadata = {
    'access_frequency': defaultdict(lambda: BASELINE_FREQUENCY),
    'priority_level': defaultdict(lambda: DEFAULT_PRIORITY),
    'load_status': defaultdict(lambda: LOAD_STATUS_FACTOR),
    'frequency_update_counter': defaultdict(lambda: time.time())
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by considering entries with the lowest priority level first, then the lowest access frequency, and finally the highest load status. If a tie occurs, the entry with the oldest real-time frequency update is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_priority = float('inf')
    min_frequency = float('inf')
    max_load_status = float('-inf')
    oldest_update = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        priority = metadata['priority_level'][key]
        frequency = metadata['access_frequency'][key]
        load_status = metadata['load_status'][key]
        update_time = metadata['frequency_update_counter'][key]

        if (priority < min_priority or
            (priority == min_priority and frequency < min_frequency) or
            (priority == min_priority and frequency == min_frequency and load_status > max_load_status) or
            (priority == min_priority and frequency == min_frequency and load_status == max_load_status and update_time < oldest_update)):
            candid_obj_key = key
            min_priority = priority
            min_frequency = frequency
            max_load_status = load_status
            oldest_update = update_time
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency of the entry is increased using adaptive frequency scaling. The priority level is adjusted to prevent priority inversion, and the real-time frequency update counter is reset to reflect the recent access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['priority_level'][key] = max(metadata['priority_level'][key], DEFAULT_PRIORITY)
    metadata['frequency_update_counter'][key] = time.time()

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency to a baseline value, assigns a default priority level, and sets the load status based on current system conditions. The real-time frequency update counter is initialized to track future accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = BASELINE_FREQUENCY
    metadata['priority_level'][key] = DEFAULT_PRIORITY
    metadata['load_status'][key] = LOAD_STATUS_FACTOR
    metadata['frequency_update_counter'][key] = time.time()

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the priority levels of remaining entries to prevent priority inversion, adjusts the load status to reflect the reduced cache load, and updates the real-time frequency update counters to ensure accurate tracking of future accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        metadata['priority_level'][key] = max(metadata['priority_level'][key] - 1, DEFAULT_PRIORITY)
        metadata['load_status'][key] = max(metadata['load_status'][key] - 0.1, 0)
        metadata['frequency_update_counter'][key] = time.time()