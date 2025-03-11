import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ParticleSimulation:
    def __init__(self, root):
        self.root = root
        self.root.title("Active Brownian Particle Simulation")
        
        # Create frames for controls and canvas
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Simulation parameters - following the paper
        self.v_label = tk.Label(self.control_frame, text="Speed (v):")
        self.v_label.grid(row=0, column=0, padx=5, pady=5)
        self.v_entry = tk.Entry(self.control_frame, width=8)
        self.v_entry.insert(0, "3.0")  # cm/s in the paper
        self.v_entry.grid(row=0, column=1, padx=5, pady=5)
        
        self.eta_label = tk.Label(self.control_frame, text="Rot. Noise (η):")
        self.eta_label.grid(row=0, column=2, padx=5, pady=5)
        self.eta_entry = tk.Entry(self.control_frame, width=8)
        self.eta_entry.insert(0, "3.0")  # rad/s in the paper
        self.eta_entry.grid(row=0, column=3, padx=5, pady=5)
        
        self.delay_label = tk.Label(self.control_frame, text="Delay Time (ε):")
        self.delay_label.grid(row=0, column=4, padx=5, pady=5)
        self.delay_entry = tk.Entry(self.control_frame, width=8)
        self.delay_entry.insert(0, "0.5")  # seconds in the paper
        self.delay_entry.grid(row=0, column=5, padx=5, pady=5)
        
        self.start_button = tk.Button(self.control_frame, text="Start Simulation", command=self.start_simulation)
        self.start_button.grid(row=0, column=6, padx=10, pady=5)
        
        self.stop_button = tk.Button(self.control_frame, text="Stop Simulation", command=self.stop_simulation, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=7, padx=5, pady=5)
        
        self.plot_button = tk.Button(self.control_frame, text="Plot MSD", command=self.plot_msd, state=tk.DISABLED)
        self.plot_button.grid(row=0, column=8, padx=5, pady=5)
        
        # Canvas for simulation
        self.width = 800
        self.height = 600
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, width=self.width, height=self.height, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Info text
        self.info_text = self.canvas.create_text(10, 10, anchor='nw', text='', font=('Arial', 10), fill='black')
        
        # Simulation variables
        self.running = False
        self.particle = None
        self.trail = []
        self.plot_window = None
        
        # ABP properties
        self.radius = 5  # visual radius of particle
        self.position = None
        self.theta = None
        self.angular_velocity = None
        self.dt = 0.01  # time step for simulation (much smaller than delay time)
        
        # Data collection for MSD
        self.positions_history = []
        self.time_points = []
        self.current_time = 0
        self.update_counter = 0
        self.next_noise_update = 0
        
    def start_simulation(self):
        # Parse parameters
        try:
            self.v = float(self.v_entry.get())  # speed
            self.eta = float(self.eta_entry.get())  # rotational noise magnitude
            self.epsilon = float(self.delay_entry.get()) * 1000  # delay time in ms
            
            # Calculate theoretical Dr based on paper formula: Dr = η²/6
            self.Dr_theoretical = (self.eta**2) / 6
            
            # Reset simulation state
            self.canvas.delete("all")
            self.info_text = self.canvas.create_text(10, 10, anchor='nw', text='', font=('Arial', 10), fill='black')
            self.trail = []
            
            # Initialize particle
            self.position = np.array([self.width/2, self.height/2], dtype=float)
            self.theta = 0.0
            self.angular_velocity = np.random.uniform(-self.eta, self.eta)
            
            # Draw particle
            self.particle = self.canvas.create_oval(
                self.position[0]-self.radius, self.position[1]-self.radius,
                self.position[0]+self.radius, self.position[1]+self.radius,
                fill='red', outline='black'
            )
            
            # Data collection
            self.positions_history = [self.position.copy()]
            self.time_points = [0]
            self.current_time = 0
            self.update_counter = 0
            self.next_noise_update = self.epsilon  # Time for next noise update
            
            # UI state
            self.running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.plot_button.config(state=tk.DISABLED)
            
            # Start animation
            self.animate()
            
        except ValueError:
            tk.messagebox.showerror("Input Error", "Please enter valid numerical values")
    
    def stop_simulation(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.plot_button.config(state=tk.NORMAL)
    
    def animate(self):
        if not self.running:
            return
        
        # Update particle position according to ABP model
        self.update_position()
        self.current_time += self.dt
        self.update_counter += 1
        
        # Record position for MSD calculation (not every step to save memory)
        if self.update_counter % 10 == 0:  # record every 10 steps
            self.positions_history.append(self.position.copy())
            self.time_points.append(self.current_time)
        
        # Update noise parameter after delay time ε
        if self.current_time * 1000 >= self.next_noise_update:
            self.angular_velocity = np.random.uniform(-self.eta, self.eta)
            self.next_noise_update += self.epsilon
        
        # Update display
        self.canvas.coords(
            self.particle,
            self.position[0]-self.radius, self.position[1]-self.radius,
            self.position[0]+self.radius, self.position[1]+self.radius
        )
        
        # Update info text
        dr_estimate = f"{self.Dr_theoretical:.4f}" if hasattr(self, 'Dr_theoretical') else "N/A"
        self.canvas.itemconfig(
            self.info_text,
            text=f'Time: {self.current_time:.2f}s\n'
                 f'Position: ({self.position[0]:.1f}, {self.position[1]:.1f})\n'
                 f'Orientation: {np.degrees(self.theta):.1f}°\n'
                 f'Speed: {self.v:.2f}\n'
                 f'Angular velocity: {self.angular_velocity:.2f} rad/s\n'
                 f'Theoretical Dr: {dr_estimate}'
        )
        
        # Continue animation
        self.root.after(10, self.animate)  # update approximately 100 fps
    
    def update_position(self):
        # Store previous position for trail
        prev_position = self.position.copy()
        
        # Update orientation based on current angular velocity
        self.theta += self.angular_velocity * self.dt
        
        # Calculate new position (constant speed v along orientation)
        velocity = np.array([
            self.v * np.cos(self.theta),
            self.v * np.sin(self.theta)
        ])
        
        # Update position
        self.position += velocity * self.dt
        
        # Handle boundary conditions - periodic boundary like in the paper
        # This is crucial for proper MSD calculation
        if self.position[0] < 0:
            self.position[0] += self.width
        elif self.position[0] > self.width:
            self.position[0] -= self.width
            
        if self.position[1] < 0:
            self.position[1] += self.height
        elif self.position[1] > self.height:
            self.position[1] -= self.height
        
        # Draw trail
        trail_segment = self.canvas.create_line(
            prev_position[0], prev_position[1], self.position[0], self.position[1],
            fill='blue', width=1
        )
        self.trail.append(trail_segment)
    
    def calculate_theoretical_msd(self, times):
        """Calculate theoretical MSD according to paper equation (4)"""
        v = self.v
        Dr = self.Dr_theoretical
        
        return 2 * (v**2 / Dr) * (times + (1/Dr) * (np.exp(-Dr * times) - 1))
    
    def calculate_msd(self):
        """Calculate MSD from simulation data using time-averaged method"""
        positions = np.array(self.positions_history)
        times = np.array(self.time_points)
        n_points = len(positions)
        
        # Calculate time differences
        max_tau_idx = min(n_points, 1000)  # Limit the max lag time to analyze
        tau_values = []
        msd_values = []
        
        for tau_idx in range(1, max_tau_idx):
            # Calculate the time lag
            tau = times[tau_idx] - times[0]
            
            # Calculate MSD for this time lag
            squared_displacements = []
            for i in range(n_points - tau_idx):
                disp = positions[i + tau_idx] - positions[i]
                
                # Handle periodic boundary crossings - adjust displacement
                if abs(disp[0]) > self.width/2:
                    disp[0] = self.width - abs(disp[0])
                if abs(disp[1]) > self.height/2:
                    disp[1] = self.height - abs(disp[1])
                    
                squared_displacements.append(np.sum(disp**2))
            
            # Average squared displacement for this time lag
            if squared_displacements:
                msd = np.mean(squared_displacements)
                tau_values.append(tau)
                msd_values.append(msd)
        
        return np.array(tau_values), np.array(msd_values)
    
    def plot_msd(self):
        # Close existing plot window if it exists
        if self.plot_window is not None and self.plot_window.winfo_exists():
            self.plot_window.destroy()
        
        # Create a new window
        self.plot_window = tk.Toplevel(self.root)
        self.plot_window.title("Mean Square Displacement Analysis")
        self.plot_window.geometry("800x600")
        
        # Create matplotlib figure
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig, master=self.plot_window)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Calculate MSD from simulation data
        tau_values, msd_values = self.calculate_msd()
        
        # Plot simulation MSD
        ax.loglog(tau_values, msd_values, 'bo', markersize=3, label='Simulation')
        
        # Calculate and plot theoretical MSD
        if hasattr(self, 'Dr_theoretical') and len(tau_values) > 0:
            theoretical_times = np.logspace(np.log10(tau_values[0]), np.log10(tau_values[-1]), 100)
            theoretical_msd = self.calculate_theoretical_msd(theoretical_times)
            ax.loglog(theoretical_times, theoretical_msd, 'r-', linewidth=2, 
                      label=f'Theory: Dr={self.Dr_theoretical:.4f}')
        
        # Find and mark the transition time (approximately 1/Dr)
        if hasattr(self, 'Dr_theoretical'):
            transition_time = 1/self.Dr_theoretical
            if tau_values[0] <= transition_time <= tau_values[-1]:
                # Mark transition point
                ax.axvline(x=transition_time, color='green', linestyle='--', alpha=0.5)
                ax.text(transition_time*1.1, ax.get_ylim()[0]*2, f'τ = 1/Dr', 
                        color='green', rotation=90, verticalalignment='bottom')
        
        # Add reference slopes
        x_ref = np.array([tau_values[0], tau_values[-1]])
        
        # Ballistic reference (τ²)
        if len(msd_values) > 2:
            ballistic_factor = msd_values[1]/(tau_values[1]**2)
            y_ballistic = ballistic_factor * x_ref**2
            ax.loglog(x_ref, y_ballistic, 'k--', alpha=0.5, linewidth=1, label='∼ τ²')
        
        # Diffusive reference (τ)
        if len(msd_values) > 10:
            diffusive_factor = msd_values[-1]/tau_values[-1]
            y_diffusive = diffusive_factor * x_ref
            ax.loglog(x_ref, y_diffusive, 'k:', alpha=0.5, linewidth=1, label='∼ τ')
        
        # Set labels and title
        ax.set_xlabel('Time (τ)')
        ax.set_ylabel('Mean Square Displacement (MSD)')
        ax.set_title('ABP Model: Transition from Ballistic to Diffusive Motion')
        ax.legend()
        ax.grid(True, which="both", linestyle='--', alpha=0.5)
        
        # Add parameter information
        param_text = f"Parameters: v = {self.v}, η = {self.eta}, ε = {self.epsilon/1000}s"
        fig.text(0.5, 0.01, param_text, ha='center')
        
        fig.tight_layout(rect=[0, 0.03, 1, 1])
        canvas.draw()
        
        # Add save button
        save_frame = tk.Frame(self.plot_window)
        save_frame.pack(pady=5)
        
        save_button = tk.Button(save_frame, text="Save Plot", 
                               command=lambda: self.save_plot(fig))
        save_button.pack()
    
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
