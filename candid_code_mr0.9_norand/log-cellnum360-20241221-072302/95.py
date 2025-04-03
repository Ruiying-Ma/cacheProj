# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_FREQUENCY = 1
READ_HEAVY_THRESHOLD = 5
WRITE_HEAVY_THRESHOLD = 2
FREQUENCY_DECAY_FACTOR = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a dynamic allocation score for each cache entry, a frequency predictor that tracks access frequency, an access category label (e.g., read-heavy, write-heavy), and a synchronized timestamp for each access.
metadata = {
    'frequency': defaultdict(lambda: BASELINE_FREQUENCY),
    'category': defaultdict(lambda: 'neutral'),
    'timestamp': {},
    'allocation_score': {}
}

def calculate_allocation_score(key):
    frequency = metadata['frequency'][key]
    timestamp = metadata['timestamp'][key]
    category = metadata['category'][key]
    
    category_weight = 1
    if category == 'read-heavy':
        category_weight = 0.5
    elif category == 'write-heavy':
        category_weight = 1.5
    
    return frequency * category_weight / (1 + timestamp)

def evict(cache_snapshot, obj):
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    
    for key in cache_snapshot.cache:
        score = calculate_allocation_score(key)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    # Your code below
    key = obj.key
    metadata['frequency'][key] += 1
    metadata['timestamp'][key] = cache_snapshot.access_count
    
    # Re-evaluate access category
    if metadata['frequency'][key] > READ_HEAVY_THRESHOLD:
        metadata['category'][key] = 'read-heavy'
    elif metadata['frequency'][key] < WRITE_HEAVY_THRESHOLD:
        metadata['category'][key] = 'write-heavy'
    else:
        metadata['category'][key] = 'neutral'

def update_after_insert(cache_snapshot, obj):
    # Your code below
    key = obj.key
    metadata['frequency'][key] = BASELINE_FREQUENCY
    metadata['timestamp'][key] = cache_snapshot.access_count
    metadata['category'][key] = 'neutral'
    metadata['allocation_score'][key] = calculate_allocation_score(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in metadata['frequency']:
        del metadata['frequency'][evicted_key]
        del metadata['timestamp'][evicted_key]
        del metadata['category'][evicted_key]
        del metadata['allocation_score'][evicted_key]
    
    # Recalibrate scores and decay frequencies
    for key in cache_snapshot.cache:
        metadata['frequency'][key] *= FREQUENCY_DECAY_FACTOR
        metadata['allocation_score'][key] = calculate_allocation_score(key)