import tkinter as tk
from tkinter import messagebox

def countdown_generator(seconds):
    """The generator holds the state of the remaining time."""
    while seconds >= 0:
        yield seconds
        seconds -= 1

class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smooth Circular Timer")
        self.root.geometry("350x420")
        self.root.config(bg="#f5f5f7")
        
        # State tracking
        self.timer_gen = None
        self.total_seconds = 0
        self.running = False
        self.paused = False
        
        # Smooth Animation Variables
        self.current_extent = 0.0  # Where the visible bar currently is
        self.target_extent = 0.0   # Where the bar is trying to animate to
        self.animation_speed = 0.15 # CSS-like ease speed (higher = faster snap)

        # Input Layout
        self.label = tk.Label(root, text="Enter seconds:", font=("Helvetica", 12), bg="#f5f5f7", fg="#333333")
        self.label.pack(pady=5)

        self.entry = tk.Entry(root, font=("Helvetica", 14), width=10, justify="center", bd=1, relief="solid")
        self.entry.pack(pady=5)
        self.entry.insert(0, "10")

        # --- CIRCULAR PROGRESS BAR ---
        self.canvas_size = 220
        self.canvas = tk.Canvas(root, width=self.canvas_size, height=self.canvas_size, bg="#f5f5f7", highlightthickness=0)
        self.canvas.pack(pady=15)

        self.arc_box = (20, 20, self.canvas_size - 20, self.canvas_size - 20)

        # Background track ring
        self.canvas.create_oval(self.arc_box, outline="#e5e5ea", width=10)

        # Foreground active progress arc (starts at 90 deg / top)
        self.progress_arc = self.canvas.create_arc(self.arc_box, start=90, extent=0, outline="#007AFF", width=10, style="arc")

        # Text Overlay
        self.time_display = self.canvas.create_text(self.canvas_size // 2, self.canvas_size // 2, text="00:00", font=("Helvetica", 32, "bold"), fill="#1c1c1e")

        # Control Buttons
        btn_frame = tk.Frame(root, bg="#f5f5f7")
        btn_frame.pack(pady=10)

        self.start_button = tk.Button(btn_frame, text="Start", command=self.start_timer, bg="#34C759", fg="white", font=("Helvetica", 10, "bold"), width=8, relief="flat")
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.pause_button = tk.Button(btn_frame, text="Pause", command=self.toggle_pause, bg="#FF9500", fg="white", font=("Helvetica", 10, "bold"), width=8, state="disabled", relief="flat")
        self.pause_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = tk.Button(btn_frame, text="Reset", command=self.reset_timer, bg="#FF3B30", fg="white", font=("Helvetica", 10, "bold"), width=8, relief="flat")
        self.reset_button.pack(side=tk.LEFT, padx=5)

    def start_timer(self):
        if not self.running:
            try:
                self.total_seconds = int(self.entry.get())
                if self.total_seconds <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid positive number.")
                return

            self.timer_gen = countdown_generator(self.total_seconds)
            self.running = True
            self.paused = False
            
            # Reset animation tracking states
            self.current_extent = 0.0
            self.target_extent = 0.0
            
            self.entry.config(state="disabled")
            self.start_button.config(state="disabled")
            self.pause_button.config(state="normal", text="Pause", bg="#FF9500")
            
            # Kickstart loops
            self.update_generator_clock()
            self.animate_frame_loop()

    def toggle_pause(self):
        if not self.running:
            return

        if not self.paused:
            self.paused = True
            self.pause_button.config(text="Resume", bg="#007AFF")
        else:
            self.paused = False
            self.pause_button.config(text="Pause", bg="#FF9500")
            self.update_generator_clock()
            self.animate_frame_loop()

    def reset_timer(self):
        self.running = False
        self.paused = False
        self.timer_gen = None 
        self.current_extent = 0.0
        self.target_extent = 0.0
        
        self.entry.config(state="normal")
        self.start_button.config(state="normal")
        self.pause_button.config(state="disabled", text="Pause", bg="#FF9500")
        
        self.canvas.itemconfig(self.time_display, text="00:00")
        self.canvas.itemconfig(self.progress_arc, extent=0)

    def update_generator_clock(self):
        """Pulls from the generator exactly once every second to adjust target metrics."""
        if self.running and not self.paused:
            try:
                remaining_time = next(self.timer_gen)
                
                # Update numerical readout
                mins, secs = divmod(remaining_time, 60)
                self.canvas.itemconfig(self.time_display, text=f"{mins:02d}:{secs:02d}")
                
                # REVERSED CLOCKWISE MATH: 
                # (1 - fraction) calculates the inverse.
                # A negative value (-360) draws the arc clockwise instead of counter-clockwise.
                fraction_elapsed = 1.0 - (remaining_time / self.total_seconds)
                self.target_extent = fraction_elapsed * -360
                
                # Schedule the next generator advancement in exactly 1 second
                self.root.after(1000, self.update_generator_clock)
                
            except StopIteration:
                self.running = False
                self.trigger_alarm()

    def animate_frame_loop(self):
        """Runs roughly 60 times a second to transition positions seamlessly."""
        if self.running and not self.paused:
            # Calculate distance to target position
            error = self.target_extent - self.current_extent
            
            # Smooth step adjustment (similar to CSS ease-out tracking)
            if abs(error) > 0.01:
                self.current_extent += error * self.animation_speed
            else:
                self.current_extent = self.target_extent

            # Apply updated frame coordinates to canvas item
            self.canvas.itemconfig(self.progress_arc, extent=self.current_extent)
            
            # Schedule next frame in 16 milliseconds (~60fps)
            self.root.after(16, self.animate_frame_loop)

    def trigger_alarm(self):
        self.entry.config(state="normal")
        self.start_button.config(state="normal")
        self.pause_button.config(state="disabled", text="Pause", bg="#FF9500")
        self.canvas.itemconfig(self.time_display, text="00:00")
        self.canvas.itemconfig(self.progress_arc, extent=-360)
        
        self.root.bell() 
        messagebox.showinfo("Time's Up!", "🚨 Timer finished! 🚨")

if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()