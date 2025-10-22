import cv2
import mediapipe as mp
import numpy as np
from mediapipe.framework.formats import landmark_pb2

class PoseDetector:
    def __init__(self, static_image_mode=False, model_complexity=2, smooth_landmarks=True):
        self.mp_pose = mp.solutions.pose
        self.mp_draw = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            smooth_landmarks=smooth_landmarks,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )
    
    def detect_pose(self, image, draw=True, keypoints_only=False):
        """
        Detect pose landmarks in the image
        """
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_image)
        
        if results.pose_landmarks and draw:
            if keypoints_only:
                keypoint_indices = [
                    11, 12, 13, 14, 15, 16, 19, 20, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32
                ]

                landmarks = results.pose_landmarks.landmark
                filtered_landmarks = [landmarks[i] for i in keypoint_indices]
                index_map = {orig: new for new, orig in enumerate(keypoint_indices)}

                original_connections = [
                    (11, 13), (13, 15),  # left arm
                    (12, 14), (14, 16),  # right arm
                    (11, 23), (12, 24),  # torso sides
                    (23, 25), (25, 27),  # left leg
                    (24, 26), (26, 28),  # right leg
                    (27, 31), (28, 32),  # heels
                    (11, 12), (23, 24),  # shoulders and hips
                    (15, 19), (16, 20),  # wrists
                    (30, 32), (29, 31),  # feet
                    (28, 32), (27, 31)   # ankles
                ]

                remapped_connections = [
                    (index_map[a], index_map[b])
                    for (a, b) in original_connections
                    if a in index_map and b in index_map
                ]

                filtered_landmarks_pb2 = landmark_pb2.NormalizedLandmarkList(
                    landmark=filtered_landmarks
                )

                self.mp_draw.draw_landmarks(
                    image,
                    filtered_landmarks_pb2,
                    remapped_connections,
                    self.mp_draw.DrawingSpec(color=(0, 128, 255), thickness=2, circle_radius=2),
                    self.mp_draw.DrawingSpec(color=(255, 255, 255), thickness=2, circle_radius=2)
                )
            else:
                self.mp_draw.draw_landmarks(
                    image, 
                    results.pose_landmarks, 
                    self.mp_pose.POSE_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(0, 128, 255), thickness=2, circle_radius=2),
                    self.mp_draw.DrawingSpec(color=(255, 255, 255), thickness=2, circle_radius=2)
                )
        
        return image, results
    
    def get_landmark_coordinates(self, results, image_shape):
        """
        Extract landmark coordinates from results
        """
        landmarks = []
        if results.pose_landmarks:
            for landmark in results.pose_landmarks.landmark:
                landmarks.append([
                    landmark.x * image_shape[1],
                    landmark.y * image_shape[0],
                    landmark.z,
                    landmark.visibility
                ])
        return np.array(landmarks)


def calculate_angle(point1, point2, point3):
    """
    Calculate angle between three points
    point1, point2, point3: [x, y] coordinates
    Returns angle in degrees
    """
    # Convert to vectors
    vector1 = np.array([point1[0] - point2[0], point1[1] - point2[1]])
    vector2 = np.array([point3[0] - point2[0], point3[1] - point2[1]])
    
    # Calculate angle
    dot_product = np.dot(vector1, vector2)
    magnitude1 = np.linalg.norm(vector1)
    magnitude2 = np.linalg.norm(vector2)
    
    # Avoid division by zero
    if magnitude1 == 0 or magnitude2 == 0:
        return 0
    
    cosine_angle = dot_product / (magnitude1 * magnitude2)
    cosine_angle = np.clip(cosine_angle, -1, 1)
    angle = np.degrees(np.arccos(cosine_angle))
    
    return angle

def calculate_angle_3d(point1, point2, point3):
    """
    Calculate angle between three 3D points
    point1, point2, point3: [x, y, z] coordinates
    Returns angle in degrees
    """
    # Convert to numpy arrays
    vector1 = np.array(point1) - np.array(point2)
    vector2 = np.array(point3) - np.array(point2)

    # Calculate angle
    dot_product = np.dot(vector1, vector2)
    magnitude1 = np.linalg.norm(vector1)
    magnitude2 = np.linalg.norm(vector2)

    # Avoid division by zero
    if magnitude1 == 0 or magnitude2 == 0:
        return 0

    cosine_angle = dot_product / (magnitude1 * magnitude2)
    # Clip to handle potential floating point inaccuracies
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
    angle = np.degrees(np.arccos(cosine_angle))

    return angle