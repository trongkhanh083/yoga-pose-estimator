import json
import os

class PoseClassifier:
    def __init__(self, reference_file=None):
        self.reference_poses = self.load_reference_poses(reference_file)

    def load_reference_poses(self, reference_file):
        """Load reference poses from file or use defaults"""
        if reference_file and os.path.exists(reference_file):
            try:
                with open(reference_file, 'r') as f:
                    loaded_poses = json.load(f)
                    return loaded_poses
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Error loading {reference_file}: {e}")

    def calculate_similarity(self, current_angles, ref_pose_data):
        """
        Calculate weighted similarity between two sets of angles.
        ref_pose_data now contains both angles and optional weights.
        """
        ref_angles = ref_pose_data
        weights = {}

        if "_weights" in ref_pose_data:
            weights = ref_pose_data["_weights"]
            # Make a copy of the angles without the weights for comparison
            ref_angles = {k: v for k, v in ref_pose_data.items() if k != "_weights"}

        common_joints = set(current_angles.keys()) & set(ref_angles.keys())
        if not common_joints:
            return 0

        weighted_errors = []
        total_weight = 0

        for joint in common_joints:
            error = abs(current_angles[joint] - ref_angles[joint])
            normalized_error = min(error / 180, 1.0)
            
            # Get weight for the joint, default to 1.0 if not specified
            weight = weights.get(joint, 1.0)
            
            weighted_errors.append((1 - normalized_error) * weight)
            total_weight += weight

        if total_weight == 0:
            return 0

        return (sum(weighted_errors) / total_weight) * 100
    
    def classify_pose(self, current_angles, threshold=30):
        """
        Classify current pose based on angle similarity
        """
        best_match = None
        best_score = 0
        
        for pose_name, ref_pose_data in self.reference_poses.items():
            score = self.calculate_similarity(current_angles, ref_pose_data)
            if score > best_score:
                best_score = score
                best_match = pose_name
        
        # Only return if similarity is above threshold
        if best_score > threshold:
            return best_match, best_score
        return "Unknown", best_score
    