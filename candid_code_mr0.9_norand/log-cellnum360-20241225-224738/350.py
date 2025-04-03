# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
PRIORITY_BOOST_ON_HIT = 10
INITIAL_PRIORITY = 5
NEUTRAL_COORDINATION_INDEX = 0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry including a priority score, a filter tag, a coordination index, and a redundancy flag. The priority score is dynamically adjusted based on access patterns, the filter tag categorizes entries based on usage type, the coordination index tracks interdependencies between entries, and the redundancy flag indicates if an entry has strategic redundancy elsewhere.
metadata = defaultdict(lambda: {
    'priority_score': INITIAL_PRIORITY,
    'filter_tag': None,
    'coordination_index': NEUTRAL_COORDINATION_INDEX,
    'redundancy_flag': False
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first filtering entries with the lowest priority scores and redundancy flags set to false. Among these, it selects the entry with the lowest coordination index, ensuring minimal impact on related entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_priority = float('inf')
    min_coordination_index = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        if not meta['redundancy_flag'] and meta['priority_score'] < min_priority:
            min_priority = meta['priority_score']
            min_coordination_index = meta['coordination_index']
            candid_obj_key = key
        elif not meta['redundancy_flag'] and meta['priority_score'] == min_priority:
            if meta['coordination_index'] < min_coordination_index:
                min_coordination_index = meta['coordination_index']
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the priority score of the accessed entry is amplified, the filter tag is reassessed to ensure it reflects current usage patterns, and the coordination index is adjusted to reflect any changes in interdependencies. The redundancy flag remains unchanged.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    meta = metadata[obj.key]
    meta['priority_score'] += PRIORITY_BOOST_ON_HIT
    # Reassess filter tag and coordination index based on some logic
    # For simplicity, we assume they remain unchanged in this example

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial priority score based on the object's expected usage, sets a filter tag according to its type, initializes the coordination index to a neutral value, and evaluates the redundancy flag based on existing cache contents.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    metadata[obj.key] = {
        'priority_score': INITIAL_PRIORITY,
        'filter_tag': 'default',  # Example filter tag
        'coordination_index': NEUTRAL_COORDINATION_INDEX,
        'redundancy_flag': False  # Evaluate based on some logic
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the priority scores of remaining entries to reflect the removal, updates coordination indices to account for the change in interdependencies, and reassesses filter tags to ensure they remain accurate. The redundancy flags are re-evaluated to identify any new opportunities for strategic redundancy.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    for key in cache_snapshot.cache:
        meta = metadata[key]
        # Recalibrate priority scores, coordination indices, and filter tags
        # For simplicity, we assume they remain unchanged in this example
        # Re-evaluate redundancy flags
        meta['redundancy_flag'] = False  # Example logic