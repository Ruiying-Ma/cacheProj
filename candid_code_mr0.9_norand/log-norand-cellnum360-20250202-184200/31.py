# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
import math

# Put tunable constant parameters below
DEFAULT_ADAPTIVE_LEARNING_RATE = 0.1
BASELINE_NEURAL_FEEDBACK_SCORE = 0.5
INITIAL_DATA_ACCESS_PREDICTOR_SCORE = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including an adaptive learning rate, a neural feedback loop score, a data access predictor score, and a historical access pattern log for each cache entry.
metadata = {
    'adaptive_learning_rate': DEFAULT_ADAPTIVE_LEARNING_RATE,
    'entries': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by combining the neural feedback loop score and the data access predictor score, prioritizing entries with lower scores and factoring in the adaptive learning rate to adjust the sensitivity of these scores over time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = math.inf
    
    for key, cached_obj in cache_snapshot.cache.items():
        entry = metadata['entries'][key]
        combined_score = (entry['neural_feedback_score'] + entry['data_access_predictor_score']) * metadata['adaptive_learning_rate']
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the historical access pattern log to reflect the recent access, adjusts the data access predictor score based on the updated pattern, and recalibrates the neural feedback loop score using the adaptive learning rate to improve future predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    entry = metadata['entries'][obj.key]
    entry['historical_access_pattern'].append(cache_snapshot.access_count)
    entry['data_access_predictor_score'] = calculate_data_access_predictor_score(entry['historical_access_pattern'])
    entry['neural_feedback_score'] = calculate_neural_feedback_score(entry['data_access_predictor_score'], metadata['adaptive_learning_rate'])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the historical access pattern log, sets an initial data access predictor score based on the object's characteristics, and assigns a baseline neural feedback loop score, all while setting the adaptive learning rate to a default value.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    metadata['entries'][obj.key] = {
        'historical_access_pattern': [cache_snapshot.access_count],
        'data_access_predictor_score': INITIAL_DATA_ACCESS_PREDICTOR_SCORE,
        'neural_feedback_score': BASELINE_NEURAL_FEEDBACK_SCORE
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalculates the adaptive learning rate to reflect the current cache dynamics, updates the neural feedback loop scores of remaining entries to account for the change, and adjusts the data access predictor scores to improve future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    del metadata['entries'][evicted_obj.key]
    metadata['adaptive_learning_rate'] = recalculate_adaptive_learning_rate(cache_snapshot)
    for key, entry in metadata['entries'].items():
        entry['neural_feedback_score'] = calculate_neural_feedback_score(entry['data_access_predictor_score'], metadata['adaptive_learning_rate'])

def calculate_data_access_predictor_score(historical_access_pattern):
    # Placeholder function to calculate data access predictor score based on historical access pattern
    return sum(historical_access_pattern) / len(historical_access_pattern)

def calculate_neural_feedback_score(data_access_predictor_score, adaptive_learning_rate):
    # Placeholder function to calculate neural feedback score
    return data_access_predictor_score * adaptive_learning_rate

def recalculate_adaptive_learning_rate(cache_snapshot):
    # Placeholder function to recalculate adaptive learning rate based on cache dynamics
    return DEFAULT_ADAPTIVE_LEARNING_RATE