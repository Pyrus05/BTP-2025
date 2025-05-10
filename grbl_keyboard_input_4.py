import serial
import time
import keyboard  # Library for capturing keyboard input
import tkinter as tk  # GUI library

# Replace 'COM11' with your serial port (e.g., '/dev/ttyUSB0' on Linux or 'COMx' on Windows)
ser = serial.Serial('/dev/ttyUSB0', 115200)
time.sleep(2)  # Wait for the connection to initialize

def send_gcode_command(command):
    command = command.strip() + '\n'
    ser.write(command.encode())  # Send G-code command
    response = ser.readline().decode().strip()  # Read GRBL's response
    print("Response:", response)


def update_gui():
    # Update the labels with the current position
    x_label.config(text=f"X: {x_current:.1f}")
    y_label.config(text=f"Y: {y_current:.1f}")
    z_label.config(text=f"Z: {z_current:.1f}")
    root.after(100, update_gui)  # Schedule the function to run every 100 ms


try:
    # Initialize GRBL by sending a newline
    ser.write(b"\r\n\r\n")
    time.sleep(2)  # Wait for GRBL to initialize
    ser.flushInput()  # Flush startup message

    # Set to relative positioning and millimeters
    send_gcode_command("G91")  # Set to relative positioning
    send_gcode_command("G21")  # Set units to millimeters

    # Initial move increment
    increment = 1  # Move 1 mm per key press

    # Variables to track the current position
    x_current, y_current, z_current = 0, 0, 0

    # Create a GUI window
    root = tk.Tk()
    root.title("GRBL Position Tracker")
    root.geometry("200x150")

    # Labels to display X, Y, Z positions
    x_label = tk.Label(root, text=f"X: {x_current:.1f}", font=("Arial", 12))
    x_label.pack(pady=5)
    y_label = tk.Label(root, text=f"Y: {y_current:.1f}", font=("Arial", 12))
    y_label.pack(pady=5)
    z_label = tk.Label(root, text=f"Z: {z_current:.1f}", font=("Arial", 12))
    z_label.pack(pady=5)

    print("Use arrow keys to move X and Y axes.")
    print("Use 'Shift' for Z up and 'Left Ctrl' for Z down.")
    print("Press '+' or '-' to increase/decrease increment. Press 'i' to set a custom value.")
    print("Press 's' to set current position as zero.")
    print("Press 'g' to go to zero position.")
    print("Press 'esc' to quit.")

    send_gcode_command("G92 X0 Y0 Z0")  # Set current position as zero
    print("Current position set as zero.")

    def control_loop():
        global increment, x_current, y_current, z_current

        # Move X and Y with arrow keys
        if keyboard.is_pressed('up'):
            y_current += increment
            send_gcode_command(f"G1 Y{increment} F500")  # Move Y+ (up)
            time.sleep(0.1)
        elif keyboard.is_pressed('down'):
            y_current -= increment
            send_gcode_command(f"G1 Y{-increment} F500")  # Move Y- (down)
            time.sleep(0.1)
        elif keyboard.is_pressed('left'):
            x_current -= increment
            send_gcode_command(f"G1 X{-increment} F500")  # Move X- (left)
            time.sleep(0.1)
        elif keyboard.is_pressed('right'):
            x_current += increment
            send_gcode_command(f"G1 X{increment} F500")  # Move X+ (right)
            time.sleep(0.1)

        # Move Z axis with Shift (up) and Left Ctrl (down)
        elif keyboard.is_pressed('shift'):
            z_current += increment
            send_gcode_command(f"G1 Z{increment} F500")  # Move Z+ (up)
            time.sleep(0.1)
        elif keyboard.is_pressed('ctrl'):
            z_current -= increment
            send_gcode_command(f"G1 Z{-increment} F500")  # Move Z- (down)
            time.sleep(0.1)

        # Increase or decrease increment
        elif keyboard.is_pressed('+'):
            increment += 1.0
            print(f"Increment increased to {increment:.1f} mm")
            time.sleep(0.2)
        elif keyboard.is_pressed('-') and increment > 0.1:
            increment -= 1.0
            print(f"Increment decreased to {increment:.1f} mm")
            time.sleep(0.2)
        # Set a custom increment value
        elif keyboard.is_pressed('i'):
            try:
                user_input = input("Enter new increment value (in mm): ").strip()
                new_increment = float(user_input)
                if new_increment > 0:  # Ensure positive increment
                    increment = new_increment
                    print(f"Increment set to {increment:.1f} mm")
                else:
                    print("Increment must be a positive number. Try again.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")
            time.sleep(0.5)  # Add a slight delay to avoid repeated input

        # Set current position as zero
        elif keyboard.is_pressed('s'):
            x_current, y_current, z_current = 0, 0, 0
            send_gcode_command("G92 X0 Y0 Z0")  # Set current position as zero
            print("Current position set as zero.")
            time.sleep(0.5)

        # Go to zero position
        elif keyboard.is_pressed('g'):
            send_gcode_command("G90")  # Switch to absolute positioning
            send_gcode_command(f"G1 X0 Y0 Z0 F500")  # Move to zero
            send_gcode_command("G91")  # Switch back to relative positioning
            x_current, y_current, z_current = 0, 0, 0
            print("Moved to zero position.")
            time.sleep(0.5)

        # Exit control
        elif keyboard.is_pressed('esc'):
            print("Exiting control.")
            root.destroy()
            return

        root.after(50, control_loop)  # Schedule the control loop to run every 50 ms

    root.after(100, update_gui)  # Start updating the GUI
    root.after(50, control_loop)  # Start the control loop
    root.mainloop()  # Run the GUI main loop

except Exception as e:
    print("Error:", e)
finally:
    ser.close()  # Close the serial connection
