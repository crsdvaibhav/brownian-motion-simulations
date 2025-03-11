import tkinter as tk
import numpy as np

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
        self.canvas.pack()
        
        # Particle properties
        self.radius = 5
        self.position = np.array([self.width/2, self.height/2], dtype=float)
        self.trail = []  # List to store trail line objects
        
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
        
        # Randomly update angular velocity after epsilon time
        self.root.after(self.epsilon, self.update_angular_velocity)

        self.animate()
    
    def update_angular_velocity(self):
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
        if (self.position[0] - self.radius <= 0 or self.position[0] + self.radius >= self.width) or self.position[1] - self.radius <= 0 or self.position[1] + self.radius >= self.height:
            self.velocity[0] = 0
            self.velocity[1] = 0
            self.angular_velocity = 0
            self.speed = 0

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
                 f'Velocity: ({self.velocity[0]:.2f}, {self.velocity[1]:.2f})'
        )

        self.root.after(16, self.animate)  # Update roughly every 16ms (60 FPS)
        

if __name__ == "__main__":
    root = tk.Tk()
    app = ParticleSimulation(root)
    root.mainloop()
        
