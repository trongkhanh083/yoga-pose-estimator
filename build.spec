# -*- mode: python ; coding: utf-8 -*-

import os
import mediapipe as mp

block_cipher = None

# Get MediaPipe package path
try:
    import mediapipe
    mediapipe_path = os.path.dirname(mediapipe.__file__)
except:
    mediapipe_path = ""

a = Analysis(
    ['yoga_pose_estimator.py'],
    pathex=[os.getcwd()],
    binaries=[],
    datas=[
        ('assets/fonts', 'assets/fonts'),
        ('assets/themes', 'assets/themes'),
        ('reference_poses_weighted.json', '.'),
        
        # Add only essential MediaPipe files
        (os.path.join(mediapipe_path, 'modules/pose_landmark/pose_landmark_cpu.binarypb'), 'mediapipe/modules/pose_landmark/'),
        (os.path.join(mediapipe_path, 'modules/pose_landmark/pose_landmark_full.tflite'), 'mediapipe/modules/pose_landmark/'),
        (os.path.join(mediapipe_path, 'modules/pose_detection/pose_detection.tflite'), 'mediapipe/modules/pose_detection/'),
        
        # Add your local Python modules
        ('pose_classifier.py', '.'),
        ('yoga_pose_analyzer.py', '.'),
        ('styles.py', '.'),
        ('pose_detector.py', '.'),
    ],
    hiddenimports=[
        'cv2', 'PIL', 'PIL.Image', 'PIL.ImageTk', 'PIL._tkinter_finder', 
        'PIL._webp', 'PIL._binary', 'PIL._util', 'PIL._imaging',
        'customtkinter', 'tkinter', 'mediapipe', 'numpy', 
        'pose_classifier', 'yoga_pose_analyzer', 'styles', 'pose_detector',
        'mediapipe.python._framework_bindings'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='YogaPoseEstimator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=True
)