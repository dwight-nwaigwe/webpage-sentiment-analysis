import tkinter as tk
from tkinter import messagebox
import threading
from PIL import Image, ImageTk  # Requires: pip install pillow
from call_gemini import my_gemini_function
from screenshot_tool import *
from load_data import *


class GeminiImageDisplayGui:
    def __init__(self, root):
        self.root = root
        self.root.title("Website sentiment analysis")
        self.root.geometry("600x620")
        self.root.configure(bg="#f5f5f7")

        # Keep a persistent reference to the image object to prevent garbage collection
        self.current_image_ref = None

        # Title / Description Label
        self.title_label = tk.Label(
            root, text="Website sentiment analysis", 
            font=("Arial", 14, "bold"), bg="#f5f5f7", fg="#333333"
        )
        self.title_label.pack(pady=(20, 5))
        
        # Subtitle Label
        self.subtitle_label = tk.Label(
            root, 
            text="Given a URL, this tool makes a map showing the sentiment reflected at the URL", 
            font=("Arial", 9, "italic"), 
            bg="#f5f5f7", 
            fg="#666666"
        )
        self.subtitle_label.pack(pady=(0, 10))

        # Textbox Label
        self.input_label = tk.Label(
            root, text="Enter URL in the form https://some-website.com:", 
            font=("Arial", 10, "bold"), bg="#f5f5f7", fg="#333333"
        )
        self.input_label.pack(anchor="w", padx=40, pady=(10, 2))

        # Text Input Box (tk.Entry)
        self.prompt_entry = tk.Entry(
            root, font=("Arial", 11), relief="solid", bd=1
        )
        self.prompt_entry.pack(fill="x", padx=40, pady=(0, 10))

        # Action Button to run your function
        self.run_btn = tk.Button(
            root, text="Make map", font=("Arial", 11, "bold"),
            bg="#1a73e8", fg="white", activebackground="#1557b0", activeforeground="white",
            relief="flat", cursor="hand2", command=self.start_thread
        )
        self.run_btn.pack(fill="x", padx=40, pady=10)

        # Status text overlay
        self.status_label = tk.Label(root,  font=("Arial", 10, "italic"), bg="#f5f5f7", fg="#666666")
        self.status_label.pack(pady=5)

        # Visual Frame Container for the image output
        self.image_display = tk.Label(
            root, bg="#e1e1e3", text="No output displayed yet.\nClick 'Run Gemini Process' above.", 
            font=("Arial", 10), justify="center"
        )
        self.image_display.pack(fill="both", expand=True, padx=40, pady=(0, 30))

    def start_thread(self):
        """Prevents UI freezing by offloading your function to a background thread."""
        # Get user input string from the entry box BEFORE jumping to the thread
        user_text = self.prompt_entry.get().strip()

        # UI updates to show loading state
        self.run_btn.config(state=tk.DISABLED, text="Processing...", bg="#cccccc")
        self.prompt_entry.config(state=tk.DISABLED)
        self.status_label.config(text="Running your Gemini script, please wait...")
        self.image_display.config(image="", text="Awaiting image output from code...")

        # Launch background thread and pass user_text into the worker
        threading.Thread(target=self.worker_process, args=(user_text,), daemon=True).start()


    def worker_process(self, prompt_text):
        """Executes your custom function with user input and sends resulting image to main thread."""
        try:
            
            take_screenshot_isolated(prompt_text,target_image_path)
            img, map_img = get_images()
            # Invoking custom function with prompt argument
            image_result = my_gemini_function(img, map_img)
            
            # If function returns a file path string instead of an image object, open it:
            if isinstance(image_result, str):
                image_result = Image.open(image_result)

            # Pass image object safely back to the main UI thread
            self.root.after(0, self.on_success, image_result)
            
        except Exception as e:
            error_msg = f"An error occurred in your code:\n{str(e)}"
            self.root.after(0, self.on_failure, error_msg)

    def on_success(self, pil_image):
        """Resizes and embeds the generated PIL Image directly into the Tkinter window."""
        try:
            if pil_image is None:
                raise ValueError("Your function returned None instead of an image layer.")

            # Dynamically resize image to fit comfortably within the app boundaries
            pil_image.thumbnail((500, 400), Image.Resampling.LANCZOS)
            
            # Convert to Tkinter-compatible layout
            self.current_image_ref = ImageTk.PhotoImage(pil_image)
            
            # Display image in the central frame
            self.image_display.config(image=self.current_image_ref, text="")
            self.status_label.config(text="Success! Output updated.")
        except Exception as e:
            messagebox.showerror("Display Error", f"Could not render the image payload:\n{str(e)}")
            self.image_display.config(image="", text="Render failed.")
            
        self.reset_btn()

        
    def on_failure(self, error_message):
        self.status_label.config(text="Quota limit reached (429).")
        self.image_display.config(image="", text="API Rate Limit Exceeded.\nPlease wait a minute and try again.")
        
        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
            messagebox.showwarning(
                "Rate Limit Exceeded", 
                "You have hit the Gemini API rate limit or quota.\n\nPlease wait 60 seconds before trying again."
            )
        else:
            messagebox.showerror("Execution Error", error_message)
            
        self.reset_btn()        
        
        

    def reset_btn(self):
        """Restores button and entry box back to active state."""
        self.run_btn.config(state=tk.NORMAL, text="Make map", bg="#1a73e8")
        self.prompt_entry.config(state=tk.NORMAL)
        
     