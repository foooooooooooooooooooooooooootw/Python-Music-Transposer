import tkinter as tk
from tkinter import messagebox, filedialog, Canvas, Scrollbar
import time 
import re

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
    print(f"Transposing note: {note} with shift: {shift}")  # DEBUG: Log the input note and shift

    # Handle B# and E# enharmonics
    if note == 'B#':
        print(f"Enharmonic B# → C with octave {note[-1]}")  # DEBUG: Log enharmonic change
        return 'C' + note[-1]  # Preserve the octave marker
    elif note == 'E#':
        print(f"Enharmonic E# → F with octave {note[-1]}")  # DEBUG: Log enharmonic change
        return 'F' + note[-1]  # Preserve the octave marker

    # Extract the octave marker (^ for upper, v for lower)
    octave_marker = ''
    if note.endswith('^'):
        octave_marker = '^'
        note = note[:-1]  # Remove the octave marker for transposition
    elif note.endswith('v'):
        octave_marker = 'v'
        note = note[:-1]  # Remove the octave marker for transposition

    print(f"Note before normalization: {note}")  # DEBUG: Log the note before normalization

    # Normalize flats to sharps (e.g., B♭ → A#)
    normalized_note = flat_to_sharp_map.get(note, note)
    print(f"Normalized Note: {normalized_note}")  # DEBUG: Log normalized note

    # Transpose the base note without accidental
    base_note = normalized_note.rstrip('#♭')  # Strip any accidentals
    accidental = normalized_note[len(base_note):]  # Get the accidental part

    print(f"Base Note: {base_note}, Accidental: {accidental}, Octave Marker: {octave_marker}")  # DEBUG: Log base note and accidental

    if base_note not in chromatic_scale:
        return note + octave_marker  # Return original note if not found
    
    index = chromatic_scale.index(base_note)
    new_index = (index + shift) % 12
    transposed_base = chromatic_scale[new_index]

    print(f"Transposed Base: {transposed_base}, Accidental: {accidental}")  # DEBUG: Log the transposed base note

    # Remove the accidental if the transposed note moves to a natural
    if accidental == '#' and transposed_base in ['C', 'F']:
        accidental = ''  # Remove sharp when transposing to C or F
    elif accidental == '♭' and transposed_base in ['B', 'E']:
        accidental = ''  # Remove flat when transposing to B or E

    transposed_note = transposed_base + accidental
    print(f"Final Transposed Note: {transposed_note}{octave_marker}")  # DEBUG: Log final transposed note

    # Return the final transposed note with the octave marker
    return transposed_note + octave_marker


def normalize_input(note):
    # Regular expression to capture the base note, optional accidental, and optional octave marker in any order
    match = re.match(r"([A-Ga-g])([#♭b]?)([v^]?)", note)

    if not match:
        print(f"Note doesn't match normalization pattern: {note}")  # DEBUG: Log if note does not match
        return note.upper()  # If it doesn't match, return the note as uppercase

    base_note, accidental, octave_marker = match.groups()

    print(f"Before normalization - Base Note: {base_note}, Accidental: {accidental}, Octave Marker: {octave_marker}")  # DEBUG

    # Special case for when accidental appears after the octave marker, e.g., "A^#"
    if not accidental and note.endswith('#'):
        accidental = '#'
    elif not accidental and note.endswith('b'):
        accidental = '♭'

    # Convert lowercase 'b' to '♭'
    accidental = accidental.replace('b', '♭')

    # Rebuild the normalized note as: BaseNote + Accidental + OctaveMarker
    normalized_note = base_note.upper() + accidental + octave_marker

    print(f"Normalized Note: {normalized_note}")  # DEBUG

    return normalized_note


def transpose_notes():
    # Get the input from the text field and instrument selection
    notes_input = notes_entry.get("1.0", tk.END).strip().split()
    instrument = instrument_var.get()
    transpose_value = instrument_transpose_map[instrument]  # Get transpose value from instrument selection
    
    # Normalize the input
    normalized_input = [normalize_input(note) for note in notes_input]
    print("Normalized Input:", normalized_input)  # DEBUG: Log normalized input

    # Define the valid notes including octave markers
    valid_notes = chromatic_scale + list(flat_to_sharp_map.keys())
    valid_notes_with_octaves = valid_notes + [note + '^' for note in valid_notes] + [note + 'v' for note in valid_notes]

    # Add sharps and flats to valid notes
    valid_notes_with_octaves += [note + '#' for note in valid_notes] + [note + '♭' for note in valid_notes]
    
    # DEBUG: Log the valid notes with octaves
    print("Valid Notes with Octaves:", valid_notes_with_octaves)
    
    # Check for invalid notes
    invalid_notes = [note for note in normalized_input if note not in valid_notes_with_octaves]
    if invalid_notes:
        messagebox.showerror("Invalid Notes", f"Invalid notes entered: {', '.join(invalid_notes)}.")
        print("Invalid Notes Detected:", invalid_notes)  # DEBUG: Log invalid notes
        return

    # Determine the shift based on concert pitch toggle
    shift = -transpose_value if concert_var.get() else transpose_value

    # DEBUG: Log the transpose shift value
    print("Transpose Shift:", shift)

    # Transpose the notes and update the output text
    transposed_notes = [transpose(note, shift) for note in normalized_input]
    print("Transposed Notes:", transposed_notes)  # DEBUG: Log transposed notes

    # Replace B# with C and E# with F in the output
    final_notes = [note.replace('B#', 'C').replace('E#', 'F') for note in transposed_notes]
    print("Final Transposed Notes (with enharmonic fixes):", final_notes)  # DEBUG

    # Set the output text box and disable editing
    output_entry.config(state='normal')  # Enable editing to set text
    output_entry.delete("1.0", tk.END)  # Clear previous output
    output_entry.insert("1.0", ' '.join(final_notes))  # Insert new output
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

        # Draw the treble clef on the leftmost side of each stave
        clef_x = 25  # X position for the clef symbol
        clef_y = staff_y_offset + staff * staff_spacing + 12  # Y position (centered vertically on the staff)
        
        # You can experiment with the font size for best appearance
        canvas.create_text(clef_x, clef_y, text='𝄞', font=('Segoe UI Symbol', 50), fill='black')


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

    extra_padding = 30
    staff_y_offset = max(calculate_staff_offset(input_notes), calculate_staff_offset(transposed_notes))
    staff_y_offset += extra_padding

    # Calculate how many staves are required based on the number of notes
    notes_per_staff = 8  # You can adjust this based on how many notes fit on each staff
    total_notes = max(len(input_notes), len(transposed_notes))
    required_staves = (total_notes // notes_per_staff) + 1

    # Adjust canvas height dynamically, but ensure a minimum size
    staff_spacing = 100  # Distance between staves
    canvas_height = max(440, required_staves * staff_spacing)  # Ensure a minimum canvas height of 440 pixels
    input_canvas.config(height=canvas_height)
    output_canvas.config(height=canvas_height)

    # Clear the canvases before redrawing
    input_canvas.delete("all")
    output_canvas.delete("all")

    # Draw staves and place notes
    for staff in range(required_staves):
        draw_staff(input_canvas, staff_y_offset, staff_spacing)
        draw_staff(output_canvas, staff_y_offset, staff_spacing)

    # Place notes for input and transposed output
    place_notes(input_canvas, input_notes, staff_spacing, staff_y_offset)
    place_notes(output_canvas, transposed_notes, staff_spacing, staff_y_offset)


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
        is_high = '^' in normalized_note  # Check for high octave
        is_low = 'v' in normalized_note    # Check for low octave
        
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
            if note_positions[base_note] < 15 or (is_high and note_positions[base_note] < 20):  # Example for high notes
                canvas.create_line(x_offset, y_position + 5, x_offset, y_position + stem_length + 10, fill="black", width=2)
            else:
                canvas.create_line(x_offset + 15, y_position + 5, x_offset + 15, y_position - stem_length, fill="black", width=2)        
                
            # Render the accidental symbol if applicable
            if is_flat:
                canvas.create_text(x_offset - 5, y_position - 3, text='♭', font=('Arial', 14), fill='black')
            elif is_sharp:
                canvas.create_text(x_offset - 5, y_position - 3, text='♯', font=('Arial', 14), fill='black')

            # Move the x position for the next note
            x_offset += 30  # Space between notes
            
            # Wrap to the next staff if the x_offset exceeds the staff width
            if x_offset > staff_width -20:
                x_offset = 50  # Reset x position for new staff
                current_staff += 1  # Move to the next staff

# Tkinter GUI setup
root = tk.Tk()
root.title("Python Music Transposer")

# Frame for input and output
frame = tk.Frame(root)
frame.pack(padx=10, pady=10, fill='both', expand=True)

# Input for notes
tk.Label(frame, text="Enter Notes (C, D, E, F, G, A, B, ♭, #):").grid(row=0, column=0, sticky='w')

# Create a frame for notes input and its scrollbar
notes_frame = tk.Frame(frame)
notes_frame.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

# Scrollbar for the input text box
notes_scrollbar = tk.Scrollbar(notes_frame)
notes_scrollbar.grid(row=0, column=1, sticky='ns')

# Create the input text box with the scrollbar
notes_entry = tk.Text(notes_frame, width=30, height=20, font=('Arial', 14), yscrollcommand=notes_scrollbar.set)
notes_entry.grid(row=0, column=0, sticky='nsew')

# Configure the frame for resizing
notes_frame.grid_rowconfigure(0, weight=1)
notes_frame.grid_columnconfigure(0, weight=1)

# Link scrollbar to text box
notes_scrollbar.config(command=notes_entry.yview)

# Output for transposed notes
tk.Label(frame, text="Transposed Notes:").grid(row=0, column=1, sticky='w')

# Create a frame for transposed notes output and its scrollbar
output_frame = tk.Frame(frame)
output_frame.grid(row=1, column=1, padx=5, pady=5, sticky='nsew')

# Scrollbar for the output text box
output_scrollbar = tk.Scrollbar(output_frame, orient=tk.VERTICAL)
output_scrollbar.grid(row=0, column=1, sticky='ns')

# Create the output text box with the scrollbar
output_entry = tk.Text(output_frame, width=30, height=20, fg="blue", font=('Arial', 14), state='disabled', yscrollcommand=output_scrollbar.set)
output_entry.grid(row=0, column=0, sticky='nsew')

# Configure grid for resizing
output_frame.grid_rowconfigure(0, weight=1)
output_frame.grid_columnconfigure(0, weight=1)

# Link scrollbar to text box
output_scrollbar.config(command=output_entry.yview)

# Labels for displaying instrument names
input_label_var = tk.StringVar(value="C")
output_label_var = tk.StringVar(value="B♭")
tk.Label(frame, textvariable=input_label_var).grid(row=2, column=0)  # Input instrument label
tk.Label(frame, textvariable=output_label_var).grid(row=2, column=1)  # Output instrument label

# Instrument selection for transpose
tk.Label(root, text="Select Instrument:").pack(pady=(10, 0))
instrument_var = tk.StringVar(value='B♭')  # Default to B♭
instrument_transpose_map = {'B♭': 2, 'E♭': -3, 'F': 7}  # Dummy instrument transpositions
tk.OptionMenu(root, instrument_var, *instrument_transpose_map.keys()).pack(pady=5)

concert_var = tk.BooleanVar()
concert_checkbox = tk.Checkbutton(root, text="Convert To/From Concert Pitch", variable=concert_var, command=lambda: update_instrument_labels())
concert_checkbox.pack(pady=5)

# Checkbox for staff overlay
staff_overlay_var = tk.BooleanVar()
staff_overlay_checkbox = tk.Checkbutton(root, text="Show Staff Overlay", variable=staff_overlay_var, command=lambda: toggle_staff_overlay())
staff_overlay_checkbox.pack(pady=5)

# Create canvases for drawing the staff
input_canvas_frame = tk.Frame(frame)
input_canvas_frame.grid(row=1, column=0, padx=5, pady=5)

input_canvas = Canvas(input_canvas_frame, width=330, height=440, bg="white")
input_canvas.grid(row=0, column=0, sticky='nsew')

input_scrollbar = tk.Scrollbar(input_canvas_frame, orient="vertical", command=input_canvas.yview)
input_scrollbar.grid(row=0, column=1, sticky='ns')

input_canvas.config(yscrollcommand=input_scrollbar.set)

# Configure grid to allow resizing
input_canvas_frame.grid_rowconfigure(0, weight=1)
input_canvas_frame.grid_columnconfigure(0, weight=1)

output_canvas_frame = tk.Frame(frame)
output_canvas_frame.grid(row=1, column=1, padx=5, pady=5)

output_canvas = Canvas(output_canvas_frame, width=330, height=440, bg="white")
output_canvas.grid(row=0, column=0, sticky='nsew')

output_canvas_scrollbar = tk.Scrollbar(output_canvas_frame, orient="vertical", command=output_canvas.yview)
output_canvas_scrollbar.grid(row=0, column=1, sticky='ns')

output_canvas.config(yscrollcommand=output_canvas_scrollbar.set)

# Configure grid to allow resizing
output_canvas_frame.grid_rowconfigure(0, weight=1)
output_canvas_frame.grid_columnconfigure(0, weight=1)

# Show the text boxes and hide the canvases
notes_frame.grid(row=1, column=0, padx=5, pady=5)  # Show the notes entry frame
output_frame.grid(row=1, column=1, padx=5, pady=5)  # Show the output entry
        
# Hide the canvases
input_canvas_frame.grid_remove()
output_canvas_frame.grid_remove()

# Toggle staff overlay visibility
def toggle_staff_overlay():
    if staff_overlay_var.get():
        # Hide the text boxes and show the canvases
        notes_frame.grid_remove()  # Hide the notes entry frame
        output_frame.grid_remove()  # Hide the output entry
        
        # Show the input and output canvases
        input_canvas_frame.grid(row=1, column=0, padx=5, pady=5)
        output_canvas_frame.grid(row=1, column=1, padx=5, pady=5)
        draw_staff_and_notes()

    else:
        # Show the text boxes and hide the canvases
        notes_frame.grid(row=1, column=0, padx=5, pady=5)  # Show the notes entry frame
        output_frame.grid(row=1, column=1, padx=5, pady=5)  # Show the output entry
        
        # Hide the canvases
        input_canvas_frame.grid_remove()
        output_canvas_frame.grid_remove()

# Buttons
tk.Button(root, text="Transpose", command=transpose_notes).pack(pady=5)
tk.Button(root, text="Save Transposed Notes", command=save_notes).pack(pady=(5, 20))

root.mainloop()
