import sys
import os
import cv2
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image

from pose_classifier import PoseClassifier
from yoga_pose_analyzer import YogaPoseAnalyzer
from styles import AppStyles

if getattr(sys, 'frozen', False):
    # Running as bundled executable
    bundle_dir = sys._MEIPASS
else:
    # Running as normal Python script
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

mediapipe_modules_path = os.path.join(bundle_dir, 'mediapipe', 'modules')
if os.path.exists(mediapipe_modules_path):
    os.environ['MEDIAPIPE_MODULE_PATH'] = mediapipe_modules_path


def resource_path(relative_path):
    """ Get absolute path to a resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

FONT_REGULAR = resource_path(os.path.join("assets", "fonts", "Roboto", "Roboto-Regular.ttf"))
FONT_MEDIUM = resource_path(os.path.join("assets", "fonts", "Roboto", "Roboto-Medium.ttf"))
CTK_SHAPES_FONT = resource_path(os.path.join("assets", "fonts", "CustomTkinter_shapes_font.otf"))
THEME_PATH = resource_path(os.path.join("assets", "themes", "dark-blue.json"))

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme(THEME_PATH)

# Register custom fonts
try:
    ctk.FontManager.load_font(FONT_REGULAR)
    ctk.FontManager.load_font(FONT_MEDIUM)
    ctk.FontManager.load_font(CTK_SHAPES_FONT)
except Exception as e:
    print("Warning: Could not load custom fonts:", e)

class YogaPoseEstimatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🧘‍♀️ Yoga Pose Estimator")
        self.root.geometry("1400x800")
        self.root.minsize(1200, 700)
        
        # Initialize components
        self.analyzer = YogaPoseAnalyzer()
        self.styles = AppStyles()
        # Initialize classifier with JSON file
        reference_file = resource_path("reference_poses_weighted.json")
        self.classifier = PoseClassifier(reference_file=reference_file)

        # Colors
        self.colors = self.styles.COLORS

        # Fonts
        self.font_title = self.styles.FONTS["title"]
        self.font_subtitle = self.styles.FONTS["subtitle"]
        self.font_body = self.styles.FONTS["body"]
        self.font_small = self.styles.FONTS["small"]
        
        # Camera variables
        self.cap = None
        self.is_camera_active = False
        self.current_image = None
        self.camera_btn = None
        
        # Create GUI
        self.create_enhanced_widgets()

        # Bind closing event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_enhanced_widgets(self):
            # Configure grid layout with better proportions
            self.root.grid_columnconfigure(0, weight=0)
            self.root.grid_columnconfigure(1, weight=1)
            self.root.grid_rowconfigure(0, weight=1)
            
            # Create enhanced sidebar
            self.create_enhanced_sidebar()
            
            # Create enhanced main content area
            self.create_enhanced_main_content()

    def create_enhanced_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(
            self.root,
            corner_radius=0,
            fg_color=("gray90", "gray15")
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=3)
        
        # Scrollable container for sidebar
        self.sidebar_scroll = ctk.CTkScrollableFrame(
            self.sidebar_frame,
            fg_color="transparent"
        )
        self.sidebar_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Enhanced logo section
        self.create_sidebar_header()
        
        # Enhanced control sections
        self.create_control_sections()
        
    def create_sidebar_header(self):
        header_frame = ctk.CTkFrame(self.sidebar_scroll, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Configuration",
            font=self.font_title,
            text_color=self.colors["secondary"],
            justify="center"
        )
        title_label.pack(pady=(0, 10))
        
        # Separator
        separator = ctk.CTkFrame(header_frame, height=2, fg_color="gray50")
        separator.pack(fill="x", pady=5)

    def create_control_sections(self):
        camera_section = self.create_section("Camera Controls", [
            {
                "text": "Start Camera",
                "command": self.toggle_camera,
                "color": self.colors["primary"],
                "hover_color": self.colors["primary_dark"]
            }
        ])
        self.camera_btn = camera_section[0]
        
        # Image Upload Section
        self.create_section("Image Analysis", [
            {
                "text": "Upload Image",
                "command": self.upload_image,
                "color": self.colors["secondary"],
                "hover_color": "#5A7DEB"
            },
            {
                "text": "Save Result",
                "command": self.save_image,
                "color": self.colors["accent"],
                "hover_color": "#FF9F33"
            }
        ])
        
        # Results Section
        self.create_results_section()
        
        # Settings Section
        self.create_settings_section()

    def create_section(self, title, buttons):
        """Create a consistent section with title and buttons"""
        # Frame for the section
        section_frame = ctk.CTkFrame(
            self.sidebar_scroll,
            corner_radius=12,
            border_width=1,
            border_color="gray50"
        )
        section_frame.pack(fill="x", pady=(0, 15))
        
        # Section title
        title_label = ctk.CTkLabel(
            section_frame,
            text=title,
            font=self.font_subtitle,
            anchor="w"
        )
        title_label.pack(fill="x", padx=15, pady=(12, 8))
        
        # Buttons
        create_buttons = []
        for btn_config in buttons:
            btn = ctk.CTkButton(
                section_frame,
                text=btn_config["text"],
                command=btn_config["command"],
                fg_color=btn_config["color"],
                hover_color=btn_config.get("hover_color", btn_config["color"]),
                font=self.font_body,
                height=40,
                width=200,
                corner_radius=8
            )
            btn.pack(padx=15, pady=5, anchor="w")
            create_buttons.append(btn)
        return create_buttons

    def create_results_section(self):
        section_frame = ctk.CTkFrame(
            self.sidebar_scroll,
            corner_radius=12,
            border_width=1,
            border_color="gray50"
        )
        section_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Section title with icon
        title_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=15, pady=(12, 8))
        
        ctk.CTkLabel(
            title_frame,
            text="Pose Analysis",
            font=self.font_subtitle,
            anchor="w"
        ).pack(side="left")
        
        # Enhanced results textbox
        self.results_text = ctk.CTkTextbox(
            section_frame,
            font=ctk.CTkFont(family="Roboto-Regular", size=14),
            corner_radius=8,
            border_width=1,
            border_color="gray50",
            activate_scrollbars=True
        )
        self.results_text.pack(fill="both", expand=True, padx=15, pady=(0, 12))
        
        # Initialize with placeholder text
        self.clear_results()

    def create_settings_section(self):
        section_frame = ctk.CTkFrame(
            self.sidebar_scroll,
            corner_radius=12,
            border_width=1,
            border_color="gray50"
        )
        section_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            section_frame,
            text="Settings",
            font=self.font_subtitle,
            anchor="w"
        ).pack(fill="x", padx=15, pady=(12, 8))
        
        # Theme selector
        theme_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        theme_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(theme_frame, text="Theme:", font=self.font_body).pack(side="left")
        
        self.theme_option = ctk.CTkOptionMenu(
            theme_frame,
            values=["Dark", "Light", "System"],
            command=self.change_theme,
            font=self.font_small,
            dropdown_font=self.font_small
        )
        self.theme_option.pack(side="right")

    def create_enhanced_main_content(self):
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Enhanced title frame
        self.create_enhanced_title()
        
        # Enhanced display area
        self.create_enhanced_display()
        
        # Enhanced status bar
        self.create_enhanced_status()

    def create_enhanced_title(self):
        title_frame = ctk.CTkFrame(
            self.main_frame, 
            height=80,
            fg_color="transparent"
        )
        title_frame.grid(row=0, column=0, sticky="ew", padx=25, pady=(20, 10))
        title_frame.grid_columnconfigure(0, weight=1)
        
        self.title_label = ctk.CTkLabel(
            title_frame,
            text="Pose Visualizer",
            font=self.font_title,
            text_color=self.colors["secondary"],
            justify="center"
        )
        self.title_label.pack(pady=(0, 10))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Real-time yoga pose estimation and analysis",
            font=self.font_small,
            text_color="gray60",
            justify="center"
        )
        subtitle_label.pack(pady=(0, 10))

    def create_enhanced_display(self):
        display_container = ctk.CTkFrame(
            self.main_frame,
            corner_radius=16,
            border_width=1,
            border_color="gray50"
        )
        display_container.grid(row=1, column=0, sticky="nsew", padx=25, pady=10)
        display_container.grid_columnconfigure(0, weight=1)
        display_container.grid_rowconfigure(0, weight=1)
        
        # Display frame with subtle background
        self.display_frame = ctk.CTkFrame(
            display_container,
            corner_radius=12
        )
        self.display_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.display_frame.grid_columnconfigure(0, weight=1)
        self.display_frame.grid_rowconfigure(0, weight=1)
        
        # Enhanced display label with better placeholder
        self.display_label = ctk.CTkLabel(
            self.display_frame,
            text=" Upload an image or start camera\n to begin pose detection and analysis",
            font=self.font_body,
            text_color="gray50",
            justify="center"
        )
        self.display_label.grid(row=0, column=0, sticky="nsew")

    def create_enhanced_status(self):
        status_frame = ctk.CTkFrame(
            self.main_frame,
            height=45,
            corner_radius=10,
            border_width=1,
            border_color="gray50"
        )
        status_frame.grid(row=2, column=0, sticky="ew", padx=25, pady=(0, 20))
        status_frame.grid_columnconfigure(0, weight=1)
        
        # Status label with icon
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready to analyze poses",
            font=self.font_small,
            anchor="w"
        )
        self.status_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        # Progress bar for operations
        self.progress_bar = ctk.CTkProgressBar(
            status_frame,
            height=4,
            width=200,
            progress_color=self.colors["primary"]
        )
        self.progress_bar.grid(row=0, column=1, padx=15, pady=10, sticky="e")
        self.progress_bar.set(0)
        self.progress_bar.grid_remove()  # Hide initially

    def clear_results(self):
        """Clear the results textbox"""
        self.results_text.delete("1.0", "end")
        self.results_text.insert("end", "No analysis results yet...")

    def change_theme(self, new_theme):
        ctk.set_appearance_mode(new_theme)
        
    def toggle_camera(self):
        if not self.is_camera_active:
            self.start_camera()
        else:
            self.stop_camera()
    
    def start_camera(self):
        self.progress_bar.grid()
        self.progress_bar.start()
        self.status_label.configure(text="Initializing camera...")
        
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not open camera")
            self.progress_bar.stop()
            self.progress_bar.grid_remove()
            return
        
        self.is_camera_active = True
        if self.camera_btn:
            self.camera_btn.configure(
                text="Stop Camera", 
                fg_color=self.colors["danger"], 
                hover_color="#FF6347"
            )
        self.status_label.configure(text="Camera active - Press 'Q' in camera window to stop")
        
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
        
        self.update_camera()
    
    def stop_camera(self):
        self.is_camera_active = False
        if self.cap:
            self.cap.release()
            self.cap = None
        if self.camera_btn:
            self.camera_btn.configure(
                text="Start Camera", 
                fg_color=self.colors["primary"], 
                hover_color=self.colors["primary_dark"]
            )
        self.status_label.configure(text="Camera stopped")
    
    def update_camera(self):
        if self.is_camera_active and self.cap:
            ret, frame = self.cap.read()
            if ret:
                # Process frame
                processed_frame, angles, _ = self.analyzer.analyze_pose(frame)
                
                # Classify pose
                if angles:
                    pose_name, confidence = self.classifier.classify_pose(angles)
                    
                    # Display information
                    cv2.putText(processed_frame, f'Pose: {pose_name}', (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(processed_frame, f'Confidence: {confidence:.1f}%', (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Show in separate window
                cv2.imshow('Yoga Pose Estimator - Live Camera', processed_frame)
                
                # Update results in GUI
                if angles:
                    pose_name, confidence = self.classifier.classify_pose(angles)
                    self.update_results_text(angles, pose_name, confidence)
            
            # Check for 'q' key press to stop camera
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop_camera()
                cv2.destroyAllWindows()
                return
            
            # Schedule next update
            self.root.after(10, self.update_camera)
        else:
            cv2.destroyAllWindows()
    
    def upload_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        
        if file_path:
            try:
                # Show progress
                self.progress_bar.grid()
                self.progress_bar.start()
                self.status_label.configure(text="Processing image...")
                
                # Read image
                image = cv2.imread(file_path)
                if image is None:
                    messagebox.showerror("Error", "Could not load image")
                    self.progress_bar.stop()
                    self.progress_bar.grid_remove()
                    return
                
                # Process image
                processed_image, angles, results = self.analyzer.analyze_pose(image)
                self.current_image = processed_image
                
                # Convert to PIL Image
                rgb_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb_image)
                
                # Resize image to fit display
                display_width = 800
                display_height = 600
                pil_image.thumbnail((display_width, display_height), Image.Resampling.LANCZOS)
                
                # Convert to CTkImage
                ctk_image = ctk.CTkImage(
                    light_image=pil_image,
                    dark_image=pil_image,
                    size=pil_image.size
                )
                
                # Update display
                self.display_label.configure(image=ctk_image, text="")
                self.display_label.image = ctk_image
                
                # Update results
                if angles:
                    pose_name, confidence = self.classifier.classify_pose(angles)
                    self.update_results_text(angles, pose_name, confidence)
                self.status_label.configure(text=f"Image processed: {os.path.basename(file_path)}")

                # Hide progress bar
                self.progress_bar.stop()
                self.progress_bar.grid_remove()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error processing image: {str(e)}")
                self.status_label.configure(text="Error processing image")
                self.progress_bar.stop()
                self.progress_bar.grid_remove()

    def save_image(self):
        if self.current_image is not None:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".jpg",
                filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")]
            )
            if file_path:
                cv2.imwrite(file_path, self.current_image)
                messagebox.showinfo("Success", f"Image saved as {file_path}")
                self.status_label.configure(text=f"Image saved: {os.path.basename(file_path)}")
        else:
            messagebox.showwarning("Warning", "No image to save")
    
    def process_frame(self, frame):
        """
        Process frame for real-time camera
        """
        # Analyze pose and get angles
        processed_frame, angles, results = self.analyzer.analyze_pose(frame)
        
        # Classify pose
        if angles:
            pose_name, confidence = self.classifier.classify_pose(angles)
            
            # Display classification result
            cv2.putText(processed_frame, f'Pose: {pose_name}', (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(processed_frame, f'Confidence: {confidence:.1f}%', (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return processed_frame, angles
    
    def update_results_text(self, angles, pose_name, confidence):
        """
        Update the results text widget with pose analysis
        """
        self.results_text.delete("1.0", "end")
        
        if not angles:
            self.results_text.insert("end", "No pose detected\n\n")
            self.results_text.insert("end", "Please ensure:\n")
            self.results_text.insert("end", "• Person is clearly visible\n")
            self.results_text.insert("end", "• Good lighting conditions\n")
            self.results_text.insert("end", "• Full body is in frame")
            return
        
        # Display results with formatting
        self.results_text.insert("end", "POSE NAME: ")
        color_tag = "success" if pose_name != "Unknown Pose" else "danger"
        self.results_text.insert("end", f"{pose_name}\n\n", color_tag)
        
        self.results_text.insert("end", "CONFIDENCE: ")
        confidence_color = "success" if confidence > 70 else "warning" if confidence > 50 else "danger"
        self.results_text.insert("end", f"{confidence:.1f}%\n\n", confidence_color)

        self.results_text.insert("end", "JOINT ANGLES:\n")
        self.results_text.insert("end", "─" * 20 + "\n")
        
        for joint, angle in angles.items():
            joint_name = joint.replace('_', ' ').title()
            self.results_text.insert("end", f"• {joint_name}: {angle:>6.1f}°\n")
        
        # Add feedback if pose is detected
        if pose_name != "Unknown Pose":
            feedback = self.provide_feedback(angles, pose_name)
            if feedback:
                self.results_text.insert("end", f"\nFEEDBACK:\n")
                self.results_text.insert("end", "─" * 20 + "\n")
                for item in feedback:
                    self.results_text.insert("end", f"• {item}\n")
        
        # Configure text colors
        self.results_text.tag_config("success", foreground=self.colors["success"])
        self.results_text.tag_config("warning", foreground=self.colors["warning"])
        self.results_text.tag_config("danger", foreground=self.colors["danger"])
    
    def provide_feedback(self, current_angles, target_pose_name):
        """
        Provide corrective feedback for yoga poses
        """
        feedback = []
        target_angles = self.classifier.reference_poses.get(target_pose_name, {})
        
        for joint, target_angle in target_angles.items():
            if joint in current_angles:
                current_angle = current_angles[joint]
                difference = abs(current_angle - target_angle)
                
                if difference > 15:
                    joint_name = joint.replace('_', ' ').title()
                    if current_angle < target_angle:
                        feedback.append(f"Straighten your {joint_name} more")
                    else:
                        feedback.append(f"Bend your {joint_name} more")
        
        return feedback
    
    def on_closing(self):
        """Clean up when closing the application"""
        self.stop_camera()
        self.root.destroy()


if __name__ == "__main__":
    root = ctk.CTk()
    app = YogaPoseEstimatorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()