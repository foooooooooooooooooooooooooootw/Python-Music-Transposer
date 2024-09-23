import tkinter as tk
from tkinter import messagebox, filedialog, Canvas
import time  # Import time module for Unix timestamp

# Transpose mapping and chromatic scale
chromatic_scale = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
flat_to_sharp_map = {
    'C♭': 'B', 'D♭': 'C#', 'E♭': 'D#', 'F♭': 'E', 'G♭': 'F#', 'A♭': 'G#', 'B♭': 'A#'
}

# Mapping instrument names to their transpose values
instrument_transpose_map = {
    'B♭': 2,    # B♭ Instrument
    'E♭': -3,   # E♭ Instrument
    'F': 7      # F Instrument
}

def transpose(note, shift):
    # Handle B# and E# enharmonics
    if note == 'B#':
        note = 'C'
    elif note == 'E#':
        note = 'F'

    # Extract the octave marker (^ for upper, v for lower)
    octave_marker = ''
    if note.endswith('^'):
        octave_marker = '^'
        note = note[:-1]  # Remove the octave marker for transposition
    elif note.endswith('v'):
        octave_marker = 'v'
        note = note[:-1]  # Remove the octave marker for transposition

    # Normalize flats to sharps (e.g., B♭ → A#)
    normalized_note = flat_to_sharp_map.get(note, note)
    
    # Transpose the normalized note
    index = chromatic_scale.index(normalized_note) if normalized_note in chromatic_scale else -1
    if index == -1:
        return note  # Return the original note if not found
    
    # Calculate the new index for the transposed note
    new_index = (index + shift) % 12
    transposed_note = chromatic_scale[new_index]
    
    # Return the transposed note with its original octave marker
    return transposed_note + octave_marker

def normalize_input(note):
    # Convert lowercase 'b' to '♭'
    note = note.replace('b', '♭')
    
    # Preserve the octave marker
    if note.endswith('^') or note.endswith('v'):
        octave_marker = note[-1]
        base_note = note[:-1].upper()  # Normalize to uppercase
        return base_note + octave_marker
    else:
        return note.upper()  # Normalize to uppercase

def transpose_notes():
    # Get the input from the text field and instrument selection
    notes_input = notes_entry.get("1.0", tk.END).strip().split()
    instrument = instrument_var.get()
    transpose_value = instrument_transpose_map[instrument]  # Get transpose value from instrument selection
    
    # Normalize the input
    normalized_input = [normalize_input(note) for note in notes_input]

    # Define the valid notes including octave markers
    valid_notes = chromatic_scale + list(flat_to_sharp_map.keys())
    valid_notes_with_octaves = valid_notes + [note + '^' for note in valid_notes] + [note + 'v' for note in valid_notes]

    # Add sharps and flats to valid notes
    valid_notes_with_octaves += [note + '#' for note in valid_notes] + [note + '♭' for note in valid_notes]

    # Check for invalid notes
    invalid_notes = [note for note in normalized_input if note not in valid_notes_with_octaves]
    if invalid_notes:
        messagebox.showerror("Invalid Notes", f"Invalid notes entered: {', '.join(invalid_notes)}.")
        return

    # Determine the shift based on concert pitch toggle
    shift = -transpose_value if concert_var.get() else transpose_value

    # Transpose the notes and update the output text
    transposed_notes = [transpose(note, shift) for note in normalized_input]

    # Set the output text box and disable editing
    output_entry.config(state='normal')  # Enable editing to set text
    output_entry.delete("1.0", tk.END)  # Clear previous output
    output_entry.insert("1.0", ' '.join(transposed_notes))  # Insert new output
    output_entry.config(state='disabled')  # Disable editing again
    
    # Update instrument labels
    update_instrument_labels()

    # If staff overlay is active, draw the staff and notes
    if staff_overlay_var.get():
        draw_staff_and_notes()

def update_instrument_labels():
    if concert_var.get():
        input_label_var.set(instrument_var.get())  # Show selected instrument on input side
        output_label_var.set("C")  # Show Concert C on output side
    else:
        input_label_var.set("C")  # Show Concert C on input side
        output_label_var.set(instrument_var.get())  # Show selected instrument on output side

def save_notes():
    if not output_entry.get("1.0", tk.END).strip():
        messagebox.showwarning("Warning", "No transposed notes to save.")
        return
    
    notes = output_entry.get("1.0", tk.END).strip()
    # Generate the default filename
    default_filename = f"{instrument_var.get()}-{int(time.time())}.txt"
    
    # Open save file dialog with the default filename
    filename = filedialog.asksaveasfilename(defaultextension=".txt",
        initialfile=default_filename,
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    
    if filename:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(notes)
        
        messagebox.showinfo("Success", f"Transposed notes saved as {filename}")

# Function to draw multiple staves
def draw_staff(canvas, staff_y_offset, staff_spacing):
    lines = 5
    line_height = 10  # Line height between staff lines

    # Draw the staff lines based on the y-offset (to make space for ledger lines)
    for staff in range(2):  # You can dynamically increase the number of staves based on notes
        for i in range(lines):
            y_position = staff_y_offset + i * line_height + staff * staff_spacing
            canvas.create_line(10, y_position, 290, y_position, fill="black")

# Define note_positions globally, so all functions can access it
# Note positions for rendering
note_positions = {
    'Cv': 45, 'Dv': 40, 'Ev': 35, 'Fv': 65, 'Gv': 60, 'Av': 55, 'Bv': 50,
    'C': 10, 'D': 5, 'E': 0, 'F': 30, 'G': 25, 'A': 20, 'B': 15,
    'C^': -25, 'D^': -35, 'E^': -30, 'F^': -5, 'G^': -10, 'A^': -15, 'B^': -20
}

def draw_staff_and_notes():
    input_notes = notes_entry.get("1.0", tk.END).strip().split()
    transposed_notes = output_entry.get("1.0", tk.END).strip().split()

    # Find the maximum offset needed to accommodate high or low notes
    extra_padding = 30
    staff_y_offset = max(calculate_staff_offset(input_notes), calculate_staff_offset(transposed_notes))
    staff_y_offset += extra_padding
    
    # Clear the canvases before redrawing
    input_canvas.delete("all")
    output_canvas.delete("all")

    # Define the spacing for staves
    staff_spacing = 100  # Distance between staves

    # Draw staves and place notes
    draw_staff(input_canvas, staff_y_offset, staff_spacing)
    draw_staff(output_canvas, staff_y_offset, staff_spacing)
    
    # Place notes for input and transposed output
    place_notes(input_canvas, input_notes, staff_spacing, staff_y_offset)
    place_notes(output_canvas, transposed_notes, staff_spacing, staff_y_offset)  # Make sure this is for the transposed notes


def calculate_staff_offset(notes):
    # Determine the minimum and maximum note positions in the input
    y_positions = [note_positions[note] for note in notes if note in note_positions]
    
    # Get the highest and lowest y-position
    min_y = min(y_positions) if y_positions else 0
    max_y = max(y_positions) if y_positions else 0

    # Calculate the offset: If min_y or max_y is outside normal staff bounds, adjust accordingly
    staff_y_offset = max(0, -min_y)  # Move the staff down if there are high notes
    return staff_y_offset

def adjust_canvas_size(canvas, notes):
    y_positions = [note_positions[note] for note in notes if note in note_positions]
    
    min_y = min(y_positions) if y_positions else 0
    max_y = max(y_positions) if y_positions else 0
    padding = 50  # Add some padding to the top and bottom

    # Adjust canvas height dynamically if notes are outside bounds
    canvas_height = max(440, max_y + padding)  # Ensure canvas is at least 440 pixels high
    canvas.config(height=canvas_height)

def draw_ledger_lines(canvas, y_position, x_offset):
    # Draw a ledger line above or below the note
    canvas.create_line(x_offset - 5, y_position + 5, x_offset + 20, y_position + 5, fill="black")

def place_notes(canvas, notes, staff_spacing, staff_y_offset):
    x_offset = 50  # Starting x position for notes
    staff_width = 290  # Maximum width of the staff
    current_staff = 0  # Track which staff we are on (for multi-staff placement)
    stem_length = 20  # Length of the stem

    for note in notes:
        normalized_note = normalize_input(note)  # Normalize to handle flats and sharps
        is_flat = '♭' in normalized_note
        is_sharp = '#' in normalized_note
        is_high = normalized_note.endswith('^')  # Check for high octave
        is_low = normalized_note.endswith('v')    # Check for low octave
        
        # Remove octave markers for note positioning
        base_note = normalized_note.rstrip('♭#^v')

        if base_note in note_positions:
            # Calculate the y-position based on the note's vertical position
            y_position = staff_y_offset + note_positions[base_note] + (current_staff * staff_spacing)

            # Draw ledger lines for high notes
            if is_high:
                y_position -= 35  # Move higher for high notes

                if base_note == "A":
                    draw_ledger_lines(canvas, y_position, x_offset)  # Line through the note
                elif base_note == 'B':
                    draw_ledger_lines(canvas, y_position + 5, x_offset) 
                elif base_note == 'C':
                    draw_ledger_lines(canvas, y_position, x_offset)
                    draw_ledger_lines(canvas, y_position + 10, x_offset)
                elif base_note == 'D':
                    draw_ledger_lines(canvas, y_position + 5, x_offset)
                    draw_ledger_lines(canvas, y_position + 15, x_offset)
                elif base_note == 'E':
                    draw_ledger_lines(canvas, y_position, x_offset)  # Line through the note
                    draw_ledger_lines(canvas, y_position + 10, x_offset)  # First line below
                    draw_ledger_lines(canvas, y_position + 20, x_offset)  # Second line below               
                
            # Draw ledger lines for low notes
            if is_low:
                y_position += 35 

                if base_note == 'C':
                    draw_ledger_lines(canvas, y_position, x_offset)
                elif base_note == 'B':
                    draw_ledger_lines(canvas, y_position - 5, x_offset) 
                elif base_note == "A":
                    draw_ledger_lines(canvas, y_position, x_offset)
                    draw_ledger_lines(canvas, y_position - 10, x_offset)
                elif base_note == "G":
                    draw_ledger_lines(canvas, y_position - 5, x_offset)
                    draw_ledger_lines(canvas, y_position - 15, x_offset)
                elif base_note == 'F':
                    draw_ledger_lines(canvas, y_position, x_offset)  # Line through the note
                    draw_ledger_lines(canvas, y_position - 10, x_offset)  # First line below
                    draw_ledger_lines(canvas, y_position - 20, x_offset)  # Second line below    
                
            
            # Draw the note as a black oval
            canvas.create_oval(x_offset, y_position, x_offset + 15, y_position + 10, fill="black")
            # Draw the stem (quarter note line)
            if note_positions[base_note] <= 20:  # Notes below the middle staff have upward stems
                canvas.create_line(x_offset + 15, y_position + 5, x_offset + 15, y_position - stem_length, fill="black", width=2)
            else:  # Notes above the middle staff have downward stems
                canvas.create_line(x_offset, y_position + 5, x_offset, y_position + stem_length + 10, fill="black", width=2)


            # Render the accidental symbol if applicable
            if is_flat:
                canvas.create_text(x_offset - 10, y_position, text='♭', font=('Arial', 14), fill='black')
            elif is_sharp:
                canvas.create_text(x_offset - 10, y_position, text='♯', font=('Arial', 14), fill='black')

            # Move the x position for the next note
            x_offset += 30  # Space between notes
            
            # Wrap to the next staff if the x_offset exceeds the staff width
            if x_offset > staff_width:
                x_offset = 50  # Reset x position for new staff
                current_staff += 1  # Move to the next staff



# Tkinter GUI setup
root = tk.Tk()
root.title("Python Music Transposer")

# Frame for input and output
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# Input for notes
tk.Label(frame, text="Enter Notes (C, D, E, F, G, A, B, ♭, #):").grid(row=0, column=0, sticky='w')
notes_entry = tk.Text(frame, width=30, height=20, font=('Arial', 14))  # Adjust height
notes_entry.grid(row=1, column=0, padx=5, pady=5)

# Output for transposed notes
tk.Label(frame, text="Transposed Notes:").grid(row=0, column=1, sticky='w')
output_entry = tk.Text(frame, width=30, height=20, fg="blue", font=('Arial', 14), state='disabled')  # Start disabled
output_entry.grid(row=1, column=1, padx=5, pady=5)

# Labels for displaying instrument names
input_label_var = tk.StringVar(value="C")
output_label_var = tk.StringVar(value="B♭")
tk.Label(frame, textvariable=input_label_var).grid(row=2, column=0)  # Input instrument label
tk.Label(frame, textvariable=output_label_var).grid(row=2, column=1)  # Output instrument label

# Instrument selection for transpose
tk.Label(root, text="Select Instrument:").pack(pady=(10, 0))
instrument_var = tk.StringVar(value='B♭')  # Default to B♭
tk.OptionMenu(root, instrument_var, *instrument_transpose_map.keys(), command=lambda _: update_instrument_labels()).pack(pady=5)

concert_var = tk.BooleanVar()
concert_checkbox = tk.Checkbutton(root, text="Convert To/From Concert Pitch", variable=concert_var, command=update_instrument_labels)
concert_checkbox.pack(pady=5)

# Checkbox for staff overlay
staff_overlay_var = tk.BooleanVar()
staff_overlay_checkbox = tk.Checkbutton(root, text="Show Staff Overlay", variable=staff_overlay_var, command=lambda: toggle_staff_overlay())
staff_overlay_checkbox.pack(pady=5)

# Create canvases for drawing the staff
input_canvas = Canvas(frame, width=330, height=440, bg="white")
input_canvas.grid(row=1, column=0, padx=5, pady=5)
input_canvas.grid_remove()  # Hide the input canvas initially

output_canvas = Canvas(frame, width=330, height=440, bg="white")
output_canvas.grid(row=1, column=1, padx=5, pady=5)
output_canvas.grid_remove()  # Hide the output canvas initially

def toggle_staff_overlay():
    if staff_overlay_var.get():
        notes_entry.grid_remove()  # Hide the notes entry
        output_entry.grid_remove()  # Hide the output entry
        input_canvas.grid(row=1, column=0, padx=5, pady=5)  # Show the input canvas
        output_canvas.grid(row=1, column=1, padx=5, pady=5)  # Show the output canvas
        draw_staff_and_notes()  # Draw staff and notes
    else:
        notes_entry.grid(row=1, column=0, padx=5, pady=5)  # Show the notes entry
        output_entry.grid(row=1, column=1, padx=5, pady=5)  # Show the output entry
        input_canvas.grid_remove()  # Hide the input canvas
        output_canvas.grid_remove()  # Hide the output canvas

# Buttons
tk.Button(root, text="Transpose", command=transpose_notes).pack(pady=5)
tk.Button(root, text="Save Transposed Notes", command=save_notes).pack(pady=(5, 20))

root.mainloop()
