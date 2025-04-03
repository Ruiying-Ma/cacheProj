# Import anything you need below
import numpy as np

# Put tunable constant parameters below
BASE_CONFIDENCE_SCORE = 0.5
LEARNING_RATE = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a neural network model that predicts the future access probability of each cache object, a confidence score for each prediction, and a transfer learning component that adapts the model based on observed access patterns in different contexts.
class NeuralNetworkModel:
    def __init__(self):
        self.weights = {}
        self.confidence_scores = {}
    
    def predict(self, obj_key):
        # Simple linear model for demonstration
        return self.weights.get(obj_key, 0.5), self.confidence_scores.get(obj_key, BASE_CONFIDENCE_SCORE)
    
    def update(self, obj_key, target, increase_confidence=True):
        prediction, confidence = self.predict(obj_key)
        error = target - prediction
        self.weights[obj_key] = prediction + LEARNING_RATE * error
        if increase_confidence:
            self.confidence_scores[obj_key] = min(1.0, confidence + LEARNING_RATE * abs(error))
        else:
            self.confidence_scores[obj_key] = max(0.0, confidence - LEARNING_RATE * abs(error))

model = NeuralNetworkModel()

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the object with the lowest predicted future access probability, adjusted by its confidence score, ensuring that objects with uncertain predictions are less likely to be evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        predicted_access, confidence = model.predict(key)
        adjusted_score = predicted_access * confidence
        if adjusted_score < min_score:
            min_score = adjusted_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the neural network model by reinforcing the prediction for the accessed object, increasing its confidence score, and adjusting the transfer learning component to better capture the current access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    model.update(obj.key, target=1.0, increase_confidence=True)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its future access probability using the neural network model, sets a baseline confidence score, and updates the transfer learning component to incorporate the new object's context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Initialize with a neutral prediction and baseline confidence
    model.weights[obj.key] = 0.5
    model.confidence_scores[obj.key] = BASE_CONFIDENCE_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy updates the neural network model by penalizing the prediction for the evicted object, decreasing its confidence score, and refining the transfer learning component to reduce similar future prediction errors.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    model.update(evicted_obj.key, target=0.0, increase_confidence=False)