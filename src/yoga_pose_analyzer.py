from src.pose_detector import PoseDetector, calculate_angle, calculate_angle_3d

class YogaPoseAnalyzer:
    def __init__(self, static_image_mode=True):
        self.detector = PoseDetector(static_image_mode=static_image_mode)
        self.joint_pairs = self.define_joint_pairs()

    def define_joint_pairs(self):
        """Define joint pairs for angle calculation"""
        return {
            'left_elbow': [11, 13, 15],
            'right_elbow': [12, 14, 16],
            'left_wrist': [13, 15, 19],
            'right_wrist': [14, 16, 20],
            'left_shoulder': [13, 11, 23],
            'right_shoulder': [14, 12, 24],
            'left_hip': [11, 23, 25],
            'right_hip': [12, 24, 26],
            'left_knee': [23, 25, 27],
            'right_knee': [24, 26, 28],
            'left_ankle': [25, 27, 31],
            'right_ankle': [26, 28, 32],
            'left_heel': [27, 29, 31],
            'right_heel': [28, 30, 32]
        }

    def get_landmark_names(self):
        """Return MediaPipe landmark names for reference"""
        return {
            11: "Left Shoulder", 12: "Right Shoulder",
            13: "Left Elbow", 14: "Right Elbow",
            15: "Left Wrist", 16: "Right Wrist",
            19: "Left Index", 20: "Right Index",
            23: "Left Hip", 24: "Right Hip",
            25: "Left Knee", 26: "Right Knee",
            27: "Left Ankle", 28: "Right Ankle",
            29: "Left Heel", 30: "Right Heel",
            31: "Left Foot Index", 32: "Right Foot Index"
        }
    
    def analyze_pose(self, image):
        """
        Analyze pose and calculate key angles
        """
        image, results = self.detector.detect_pose(image, keypoints_only=True)
        angles = {}
        
        if results.pose_landmarks:
            landmarks = self.detector.get_landmark_coordinates(results, image.shape)
            
            # Calculate angles for each joint pair
            for joint_name, indices in self.joint_pairs.items():
                # Pass the first 3 elements (x, y, z) of the landmarks
                points = [landmarks[idx][:3] for idx in indices]
                # Use the new 3D angle calculation
                angle = calculate_angle_3d(points[0], points[1], points[2])
                angles[joint_name] = angle
        
        return image, angles, results