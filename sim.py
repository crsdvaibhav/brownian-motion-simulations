import tkinter as tk
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ParticleSimulation:
    def __init__(self, root):
        self.root = root
        self.root.title("Particle Simulation")
        
        self.width = 600
        self.height = 400
        
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg='white')
        self.info_text = self.canvas.create_text(
            10, 10, anchor='nw', fill='black',
            text='', font=('Arial', 10)
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Add a stop button
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(fill=tk.X)
        
        self.running = True
        self.stop_button = tk.Button(self.control_frame, text="Stop Simulation", command=self.toggle_simulation)
        self.stop_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.plot_button = tk.Button(self.control_frame, text="Plot MSD", command=self.open_plot_window, state=tk.DISABLED)
        self.plot_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Particle properties
        self.radius = 5
        self.position = np.array([self.width/2, self.height/2], dtype=float)
        self.initial_position = self.position.copy()  # Store initial position for MSD calculation
        self.trail = []  # List to store trail line objects
        
        # MSD calculation variables
        self.positions_history = [self.position.copy()]  # Store all positions for MSD calculation
        self.time_steps = [0]  # Time steps corresponding to positions
        self.current_time = 0
        self.msd_values = [0]  # MSD values over time
        
        self.theta = 0.0
        self.neta = 0.1  # Define the range for angular velocity
        self.angular_velocity = np.random.uniform(-self.neta, self.neta) 
        
        self.epsilon = 500  # Time interval in milliseconds for updating angular velocity
        
        self.speed = 0.4 # Activity
        self.velocity = np.array([
            self.speed * np.cos(self.theta),
            self.speed * np.sin(self.theta)
        ])
        
        # Just paint the particle on the canvas
        self.particle = self.canvas.create_oval(
            self.position[0]-self.radius, self.position[1]-self.radius,
            self.position[0]+self.radius, self.position[1]+self.radius,
            fill='red'
        )

        # Plot window reference
        self.plot_window = None
        
        # Randomly update angular velocity after epsilon time
        self.root.after(self.epsilon, self.update_angular_velocity)

        self.animate()
    
    def update_angular_velocity(self):
        if self.running:
            self.angular_velocity = np.random.uniform(-self.neta, self.neta)
            self.root.after(self.epsilon, self.update_angular_velocity)

    def update_position(self):
        prev_position = self.position.copy()  # Store previous position

        self.theta += self.angular_velocity
        self.velocity = np.array([
            self.speed * np.cos(self.theta),
            self.speed * np.sin(self.theta)
        ])

        self.position += self.velocity
        
        # Check for collisions with walls (currently stopping at walls)
        if (self.position[0] - self.radius <= 0 or self.position[0] + self.radius >= self.width) or (self.position[1] - self.radius <= 0 or self.position[1] + self.radius >= self.height):
            self.velocity[0] = 0
            self.velocity[1] = 0
            self.angular_velocity = 0
            self.speed = 0
            self.running = False
            self.stop_button.config(text="Stopped")
            self.plot_button.config(state=tk.NORMAL)

        # Update MSD calculation data
        self.current_time += 1
        self.positions_history.append(self.position.copy())
        self.time_steps.append(self.current_time)
        
        # Calculate current MSD
        displacement = self.position - self.initial_position
        squared_displacement = np.sum(displacement**2)
        self.msd_values.append(squared_displacement)
        
        # Draw trail (line from previous position to new position)
        trail_segment = self.canvas.create_line(
            prev_position[0], prev_position[1], self.position[0], self.position[1],
            fill='blue', width=1
        )
        self.trail.append(trail_segment)

        # Optional: Limit trail length for visual clarity
        if len(self.trail) > 1000:  # Adjust this to control the fade effect
            self.canvas.delete(self.trail.pop(0))
    
    def animate(self):
        if self.running:
            self.update_position()
            
            # Display on canvas
            self.canvas.coords(
                self.particle,
                self.position[0]-self.radius, self.position[1]-self.radius,
                self.position[0]+self.radius, self.position[1]+self.radius
            )

            self.canvas.itemconfig(
                self.info_text,
                text=f'Position: ({self.position[0]:.1f}, {self.position[1]:.1f})\n'
                     f'Theta: {self.theta:.2f}\n'
                     f'Angular Velocity: {self.angular_velocity:.2f}\n'
                     f'Velocity: ({self.velocity[0]:.2f}, {self.velocity[1]:.2f})\n'
                     f'Time: {self.current_time}\n'
                     f'Current MSD: {self.msd_values[-1]:.2f}'
            )

            self.root.after(16, self.animate)  # Update roughly every 16ms (60 FPS)
    
    def toggle_simulation(self):
        self.running = not self.running
        if self.running:
            self.stop_button.config(text="Stop Simulation")
            self.plot_button.config(state=tk.DISABLED)
            self.animate()
        else:
            self.stop_button.config(text="Stopped")
            self.plot_button.config(state=tk.NORMAL)

    def calculate_msd(self):
        """Calculate MSD for all time intervals"""
        time_points = np.array(self.time_steps)
        positions = np.array(self.positions_history)
        
        # Calculate ensemble-averaged MSD (here we only have one particle, so it's just the squared displacement)
        msd = np.zeros_like(time_points, dtype=float)
        
        # For each time point, calculate MSD
        for i, t in enumerate(time_points):
            if i == 0:
                msd[i] = 0
                continue
                
            # Calculate squared displacement from initial position
            displacement = positions[i] - positions[0]
            msd[i] = np.sum(displacement**2)
            
        return time_points, msd
    
    def open_plot_window(self):
        """Open a new window with the MSD plot"""
        # Close existing plot window if it exists
        if self.plot_window is not None and self.plot_window.winfo_exists():
            self.plot_window.destroy()
        
        # Create a new window
        self.plot_window = tk.Toplevel(self.root)
        self.plot_window.title("MSD Analysis")
        self.plot_window.geometry("800x600")
        
        # Create matplotlib figure and canvas for MSD plot
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)
        canvas_plot = FigureCanvasTkAgg(fig, master=self.plot_window)
        canvas_plot.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Get MSD data
        time_points, msd = self.calculate_msd()
        
        # Filter out zero values for log-log plot
        valid_indices = np.where(time_points > 0)
        time_points = time_points[valid_indices]
        msd = msd[valid_indices]
        
        # Plot MSD vs time in log-log scale
        ax.loglog(time_points, msd, 'bo-', markersize=3, linewidth=1)
        
        # Fit a power law to the data
        if len(time_points) > 10:  # Need enough points for a meaningful fit
            log_time = np.log(time_points)
            log_msd = np.log(msd)
            
            # Linear fit in log-log space
            coeffs = np.polyfit(log_time, log_msd, 1)
            
            # The slope is the exponent in the power law: MSD ~ t^alpha
            alpha = coeffs[0]
            
            # Plot the fit line
            fit_line = np.exp(coeffs[1]) * time_points**alpha
            ax.loglog(time_points, fit_line, 'r-', linewidth=1.5, 
                      label=f'Fit: MSD ~ t^{alpha:.2f}')
            
            # Interpret the motion type based on alpha
            motion_type = "Unknown"
            if alpha < 0.9:
                motion_type = "Sub-diffusive"
            elif 0.9 <= alpha <= 1.1:
                motion_type = "Normal diffusion"
            elif 1.1 < alpha < 1.9:
                motion_type = "Super-diffusive"
            elif alpha >= 1.9:
                motion_type = "Ballistic motion"
                
            ax.text(0.05, 0.05, f"α = {alpha:.2f}\nMotion: {motion_type}", 
                    transform=ax.transAxes, bbox=dict(facecolor='white', alpha=0.8))
        
        ax.set_xlabel('Time')
        ax.set_ylabel('MSD')
        ax.set_title('Mean Square Displacement vs Time (Log-Log Scale)')
        ax.grid(True, which="both", ls="-", alpha=0.2)
        
        if len(time_points) > 10:
            ax.legend()
            
        fig.tight_layout()
        canvas_plot.draw()
        
        # Add save button
        save_frame = tk.Frame(self.plot_window)
        save_frame.pack(fill=tk.X, pady=10)
        
        save_button = tk.Button(save_frame, text="Save Plot", 
                               command=lambda: self.save_plot(fig))
        save_button.pack(side=tk.RIGHT, padx=10)
        
    def save_plot(self, fig):
        """Save the plot to a file"""
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if file_path:
            fig.savefig(file_path, dpi=300, bbox_inches='tight')
            tk.messagebox.showinfo("Save Successful", f"Plot saved to {file_path}")

        

if __name__ == "__main__":
    root = tk.Tk()
    app = ParticleSimulation(root)
    root.mainloop()
        
