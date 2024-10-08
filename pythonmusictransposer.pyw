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

def normalize_input(note):
    """Normalize both scientific and caret notation correctly based on the input format."""
    
    # Check for both caret and scientific notation in the input
    has_number = any(char.isdigit() for char in note)
    has_caret = '^' in note or 'v' in note

    # Disallow input with both number and caret notation
    if has_number and has_caret:
        raise ValueError("Invalid input: cannot have both number and caret notation.")

    # If scientific notation (contains a number), handle it
    if has_number:
        scientific_match = re.match(r'([A-G][#b♭]?)(\d+)', note)
        if scientific_match:
            base_note = scientific_match.group(1)  # Base note (e.g., 'B', 'G#', 'G♭')
            octave = scientific_match.group(2)      # Octave (e.g., '5')

            # Normalize flats
            if 'b' in base_note:
                base_note = base_note.replace('b', '♭')  

            return f"{base_note}{octave}"  # Return in the format BaseNoteOctave (e.g., G♭4)

    # If caret notation (no number), handle it
    if not has_number:
        caret_match = re.match(r'([A-G][#b♭]*)([v^]*)', note)
        if caret_match:
            base_note = caret_match.group(1)  # e.g., A, B#, C♭
            octave_modifiers = caret_match.group(2)  # e.g., ^^ or vv

            if 'b' in base_note:
                base_note = base_note.replace('b', '♭')  # Normalize flats

            # Default to octave 5 for notes A, B, G, F; octave 4 for C, D, E
            octave = 4 if base_note[0] in ['A', 'B', 'G', 'F'] else 5
            
            # Adjust the octave based on caret modifiers
            octave += octave_modifiers.count('^') - octave_modifiers.count('v')

            return f"{base_note}{octave}"

    return note  # Return as is if no match

def parse_input(input_str):
    """Parse input for both caret and scientific notation."""
    notes = input_str.split()  # Split by spaces
    parsed_notes = [normalize_input(note) for note in notes]
    return parsed_notes

def transpose_note_with_octave(note, shift):
    """Transpose a note by a certain shift, adjusting for octave and handling enharmonics."""
    # Step 1: Separate the note and the octave using regex
    match = re.match(r'([A-G][#♭]*)(\d)', note)
    if not match:
        raise ValueError(f"Invalid note format: {note}")

    note_base = match.group(1)  # Get the base note (e.g., 'A#')
    octave = int(match.group(2))  # Get the octave number (e.g., '5')

    # Debugging output to see what is being parsed
    print(f"Debug: Parsed Note - Base: {note_base}, Octave: {octave}")

    # Ensure the note base is correctly processed for sharps and flats
    note_base = flat_to_sharp_map.get(note_base, note_base)

    # Find the note's index in the chromatic scale
    try:
        note_index = chromatic_scale.index(note_base)
    except ValueError:
        raise ValueError(f"Note {note_base} is not in the chromatic scale.")

    # Calculate the new note index and handle octave shift
    new_note_index = note_index + shift

    # Debugging output for indices
    print(f"Debug: Original Note Index: {note_index}, Shift: {shift}, New Note Index: {new_note_index}")

    # Adjust the octave if the note index goes out of the chromatic scale bounds
    if new_note_index >= len(chromatic_scale):
        new_note_index -= len(chromatic_scale)
        octave += 1  # Increment octave when crossing from 'B' to 'C'
    elif new_note_index < 0:
        new_note_index += len(chromatic_scale)
        octave -= 1  # Decrement octave when crossing from 'C' to 'B'

    # Get the transposed note
    transposed_note = chromatic_scale[new_note_index]

    # Debugging output to see the final transposition
    print(f"Debug: Transposed Note: {transposed_note}, New Octave: {octave}")

    # Return the transposed note with the correct octave
    return f"{transposed_note}{octave}"


def format_output(notes, caret_notation):
    """Formats the transposed notes either in caret notation or scientific notation."""
    if caret_notation:
        return " ".join([scientific_to_caret(note) for note in notes])
    else:
        return " ".join(notes)  # Keep scientific notation as-is

def display_transposed_notes():
    notes_input = notes_entry.get("1.0", tk.END).strip()
    instrument = instrument_var.get()
    transpose_value = instrument_transpose_map[instrument]  # Get transpose value from instrument selection

    parsed_notes = parse_input(notes_input)
    print(f"Parsed Notes: {parsed_notes}")  # Debugging output

    shift = -transpose_value if concert_var.get() else transpose_value
    print(f"Shift Value: {shift}")  # Debugging output

    transposed_notes = []
    invalid_notes = []  # List to store invalid notes

    for note in parsed_notes:
        try:
            transposed_note = transpose_note_with_octave(note, shift)
            transposed_notes.append(transposed_note)
        except ValueError:
            invalid_notes.append(note)  # Collect invalid notes

    print(f"Transposed Notes: {transposed_notes}")  # Debugging output

    caret_notation = caret_var.get()
    formatted = format_output(transposed_notes, caret_notation)

    output_entry.config(state='normal')
    output_entry.delete('1.0', tk.END)
    output_entry.insert(tk.END, formatted)
    output_entry.config(state='disabled')

    # Reset the input box background to white
    notes_entry.config(bg='white')

    # Highlight invalid notes in red
    if invalid_notes:
        highlight_invalid_notes(invalid_notes)

        # Show a message box notifying the user
        messagebox.showinfo("Invalid Notes", "There are invalid notes, check highlights.")

    if staff_overlay_var.get():
        draw_staff_and_notes()

def highlight_invalid_notes(invalid_notes):
    """Highlights the invalid notes in the input box."""
    notes_input = notes_entry.get("1.0", tk.END)
    start_index = 0  # Start from the beginning of the input box

    # Reset any previous highlights
    notes_entry.tag_remove("highlight", "1.0", "end")

    # Iterate through invalid notes and highlight them
    for note in invalid_notes:
        note_index = notes_input.find(note, start_index)  # Find the note's position
        while note_index != -1:  # While we find the note
            start_pos = f"1.0 + {note_index} chars"
            end_pos = f"1.0 + {note_index + len(note)} chars"
            notes_entry.tag_add("highlight", start_pos, end_pos)  # Highlight the note
            start_index = note_index + len(note)  # Move to the end of the found note
            note_index = notes_input.find(note, start_index)  # Find next occurrence

    # Configure the highlight tag
    notes_entry.tag_config("highlight", background="#FF8C8A")  # Set highlight color


# Add caret to scientific conversion function
def scientific_to_caret(note):
    """Converts a scientific notation note to caret notation based on custom logic."""
    base_note = note[:-1]  # Extract the base note (e.g., 'F#5' -> 'F#')
    octave = int(note[-1])  # Extract the octave (e.g., 'F#5' -> 5)

    caret_modifier = ''

    # No caret or 'v' for these specific cases
    if (base_note in ['F', 'G', 'A', 'B'] and octave == 4) or (base_note in ['C', 'D', 'E'] and octave == 5):
        caret_modifier = ''
    # Handle notes that need caret modifiers
    elif octave > 5 or (octave == 5 and base_note in ['F', 'F#', 'G', 'G#', 'A', 'A#', 'B']):
        caret_modifier = '^' * (octave - 5 + (1 if base_note in ['F', 'F#', 'G', 'G#', 'A', 'A#', 'B'] else 0))
    elif octave < 4 or (octave == 4 and base_note in ['C', 'C#', 'D', 'D#', 'E']):
        caret_modifier = 'v' * (4 - octave + (1 if base_note in ['C', 'C#', 'D', 'D#', 'E'] else 0))

    return f"{base_note}{caret_modifier}"


def update_instrument_labels():
    """Update instrument labels based on the concert pitch toggle."""
    if concert_var.get():
        input_label_var.set(instrument_var.get())  # Show selected instrument on input side
        output_label_var.set("C")  # Show Concert C on output side
    else:
        input_label_var.set("C")  # Show Concert C on input side
        output_label_var.set(instrument_var.get())  # Show selected instrument on output side

def save_notes():
    """Save the transposed notes to a text file."""
    if not output_entry.get("1.0", tk.END).strip():
        messagebox.showwarning("Warning", "No transposed notes to save.")
        return

    notes = output_entry.get("1.0", tk.END).strip()
    default_filename = f"{instrument_var.get()}-{int(time.time())}.txt"

    filename = filedialog.asksaveasfilename(defaultextension=".txt",
                                            initialfile=default_filename,
                                            filetypes=[("Text files", "*.txt"), ("All files", "*.*")])

    if filename:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(notes)

        messagebox.showinfo("Success", f"Transposed notes saved as {filename}")

# Tkinter GUI setup
root = tk.Tk()
root.title("Python Music Transposer")

# Frame for input and output
frame = tk.Frame(root)
frame.pack(padx=10, pady=10, fill='both', expand=True)

# Input for notes
tk.Label(frame, text="Enter Notes (C4, D#, G^, etc.):").grid(row=0, column=0, sticky='w')

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
output_entry = tk.Text(output_frame, width=30, height=20, fg="blue", font=('DejaVu Sans', 14), state='disabled', yscrollcommand=output_scrollbar.set)
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
tk.OptionMenu(root, instrument_var, *instrument_transpose_map.keys(), command=lambda _: update_instrument_labels()).pack(pady=5)

concert_var = tk.BooleanVar()
concert_checkbox = tk.Checkbutton(root, text="Convert To/From Concert Pitch", variable=concert_var, command=update_instrument_labels)
concert_checkbox.pack(pady=5)

# Checkbox for staff overlay
staff_overlay_var = tk.BooleanVar()
staff_overlay_checkbox = tk.Checkbutton(root, text="Show Staff Overlay", variable=staff_overlay_var, command=lambda: toggle_staff_overlay())
staff_overlay_checkbox.pack(pady=5)

caret_var = tk.BooleanVar()

caret_checkbox = tk.Checkbutton(root, text="Caret Notation", variable=caret_var)
caret_checkbox.pack(pady=5)  # Adjust side, padx, pady based on your layout

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

notes_frame.grid(row=1, column=0, padx=5, pady=5)
output_frame.grid(row=1, column=1, padx=5, pady=5)
input_canvas_frame.grid_remove()
output_canvas_frame.grid_remove()

# Function to toggle staff overlay visibility
def toggle_staff_overlay():
    if staff_overlay_var.get():
        # Hide the text boxes and show the canvases
        notes_frame.grid_remove()
        output_frame.grid_remove()
        input_canvas_frame.grid(row=1, column=0, padx=5, pady=5)
        output_canvas_frame.grid(row=1, column=1, padx=5, pady=5)
        draw_staff_and_notes()
    else:
        # Show the text boxes and hide the canvases
        notes_frame.grid(row=1, column=0, padx=5, pady=5)
        output_frame.grid(row=1, column=1, padx=5, pady=5)
        input_canvas_frame.grid_remove()
        output_canvas_frame.grid_remove()

# Functions for drawing staves and notes
def draw_staff(canvas, staff_y_offset, staff_spacing):
    lines = 5
    line_height = 10
    note_spacing = 30

    for staff in range(2):  # Draw multiple staves as needed
        for i in range(lines):
            y_position = staff_y_offset + i * line_height + staff * staff_spacing
            canvas.create_line(10, y_position, 290, y_position, fill="black")

        # Treble clef
        canvas.create_text(25, staff_y_offset + staff * staff_spacing + 12, text='𝄞', font=('Segoe UI Symbol', 50), fill='black')
        
        for note_index in range(1, 3):  # Start at 1 to avoid the first measure
            line_x = 48 + (note_spacing * 4 * note_index)  # Calculate x position for the measure line

            # Draw the measure line only within the staff's vertical space
            canvas.create_line(line_x, y_position, line_x, y_position - 40, fill="black", width=2)  # Set width to 3 for a thick line

def draw_staff_and_notes():
    input_notes = notes_entry.get("1.0", tk.END).strip().split()
    transposed_notes = output_entry.get("1.0", tk.END).strip().split()
    extra_padding = 30
    staff_spacing = 100
    max_notes_per_staff = 8  # Define how many notes can fit in one staff

    # Calculate how many staves are needed based on the number of notes
    total_notes = len(input_notes) + len(transposed_notes)
    num_staves = (total_notes // max_notes_per_staff) + 1  # Add one more for any remaining notes

    staff_y_offset = max(calculate_staff_offset(input_notes), calculate_staff_offset(transposed_notes)) + extra_padding
    input_canvas.delete("all")
    output_canvas.delete("all")
    
    # Draw the required number of staves
    for staff in range(num_staves):
        draw_staff(input_canvas, staff_y_offset + staff * staff_spacing, staff_spacing)
        draw_staff(output_canvas, staff_y_offset + staff * staff_spacing, staff_spacing)

    place_notes(input_canvas, input_notes, staff_spacing, staff_y_offset)
    place_notes(output_canvas, transposed_notes, staff_spacing, staff_y_offset)

    # Update the scroll region to encompass the drawn content
    total_height = staff_y_offset + num_staves * staff_spacing
    input_canvas.config(scrollregion=(0, 0, 330, total_height))
    output_canvas.config(scrollregion=(0, 0, 330, total_height))

def calculate_staff_offset(notes):
    return 30  # Basic offset for positioning

def draw_ledger_lines(canvas, y_position, x_offset):
    # Draw a ledger line above or below the note
    canvas.create_line(x_offset - 5, y_position + 5, x_offset + 20, y_position + 5, fill="black")

# Updated note_positions to include both sharps and flats
note_positions = {
    # Octave 3
    'F3': 65, 'F#3': 65, 'G3': 60, 'G#3': 60, 'A3': 55, 'A#3': 55, 'B3': 50, 
    'Db3': 45, 'D♭3': 45, 'Eb3': 40, 'E♭3': 40, 'Gb3': 65, 'G♭3': 65, 'Ab3': 60, 'A♭3':60, 'Bb3': 55, 'B♭3':55,  # Flats for Octave 3

    # Octave 4 
    'C4': 45, 'C#4': 45, 'D4': 40, 'D#4': 40, 'E4': 35, 'F4': 30, 'F#4': 30, 'G4': 25, 'G#4': 25, 'A4': 20, 'A#4': 20, 'B4': 15,
    'Db4': 10, 'Eb4': 5, 'Gb4': 30, 'Ab4': 25, 'Bb4': 20,'D♭4': 10, 'E♭4': 5, 'G♭4': 30, 'A♭4': 25, 'B♭4': 20, 'Cb4': 45, 'C♭4': 45, # Flats for Octave 4

    # Octave 5 (Within treble staves)
    'C5': 10, 'C#5': 10, 'D5': 5, 'D#5': 5, 'E5': 0, 'F5': -5, 'F#5': -5, 'G5': -10, 'G#5': -10, 'A5': -15, 'A#5': -15, 'B5': -20,
    'Db5': 5, 'Eb5': 0, 'Gb5': -10, 'Ab5': -15, 'Bb5': -20, 'D♭5': 5, 'E♭5': 0, 'G♭5': -10, 'A♭5': -15, 'B♭5': -20, 'Cb5': 10,'C♭5': 10, # Flats for Octave 5

    # Octave 6
    'C6': -25, 'C#6': -25, 'D6': -30, 'D#6': -30, 'E6': -35, 'Db6': -30, 'Eb6': -35, 'D♭6': -30, 'E♭6': -35, 'Cb6': -25, 'C♭6': -25 # Flats for Octave 6
}

# Updated place_notes function to correctly render sharps and flats
def place_notes(canvas, notes, staff_spacing, staff_y_offset):
    x_offset = 50  # Starting x position for notes
    staff_width = 290  # Maximum width of the staff
    current_staff = 0  # Track which staff we are on (for multi-staff placement)
    stem_length = 20  # Length of the stem

    for note in notes:
        # Normalize caret or scientific notation
        normalized_note = normalize_input(note)
        print(f"Normalized Note: {normalized_note}")  # Debug statement to check the normalized note
        

        # Now directly check for the note in the expanded `note_positions` including sharps and flats
        if normalized_note in note_positions:
            y_position = staff_y_offset + note_positions[normalized_note] + (current_staff * staff_spacing)

            # Draw the note as a black oval
            canvas.create_oval(x_offset, y_position, x_offset + 15, y_position + 10, fill="black")

            # Draw the stem (quarter note line)
            if note_positions[normalized_note] < 15:
                canvas.create_line(x_offset, y_position + 5, x_offset, y_position + stem_length + 10, fill="black", width=2)
            else:
                canvas.create_line(x_offset + 15, y_position + 5, x_offset + 15, y_position - stem_length, fill="black", width=2)

            # Render the accidental symbol if applicable
            if '♭' in normalized_note or 'b' in normalized_note:  # Handle flats
                canvas.create_text(x_offset - 5, y_position - 3, text='♭', font=('Arial', 14), fill='#0000FF')
            elif '♯' in normalized_note or '#' in normalized_note:  # Handle sharps
                canvas.create_text(x_offset - 5, y_position - 3, text='♯', font=('Arial', 14), fill='#0000FF')

            # Debugging output for note and octave
            base_note = normalized_note[:-1]  # Base note (e.g., 'B')
            octave = int(normalized_note[-1])  # Octave (e.g., '5')
            print(f"Rendering Note: {base_note}, Octave: {octave}")
            
            if normalized_note == "A5":
                    draw_ledger_lines(canvas, y_position, x_offset)  # Line through the note
            elif "A3" in normalized_note or "A#3" in normalized_note or "A♭3" in normalized_note:
                    draw_ledger_lines(canvas, y_position, x_offset)
                    draw_ledger_lines(canvas, y_position - 10, x_offset)
            elif 'B5' in normalized_note or "B#5" in normalized_note or "B♭5" in normalized_note:
                    draw_ledger_lines(canvas, y_position + 5, x_offset)
            elif 'B3' in normalized_note or "B#3" in normalized_note or "B♭3" in normalized_note:
                    draw_ledger_lines(canvas, y_position - 5, x_offset)        
            elif 'C4' in normalized_note or "C#4" in normalized_note or "C♭4" in normalized_note:
                draw_ledger_lines(canvas, y_position, x_offset)
            elif 'C6' in normalized_note or "C#6" in normalized_note or "C♭6" in normalized_note:
                    draw_ledger_lines(canvas, y_position, x_offset)
                    draw_ledger_lines(canvas, y_position + 10, x_offset)
            elif 'D6' in normalized_note or "D#6" in normalized_note or "D♭6" in normalized_note:
                    draw_ledger_lines(canvas, y_position + 5, x_offset)
                    draw_ledger_lines(canvas, y_position + 15, x_offset)
            elif 'E6' in normalized_note or "E#6" in normalized_note or "E♭6" in normalized_note:
                    draw_ledger_lines(canvas, y_position, x_offset)  # Line through the note
                    draw_ledger_lines(canvas, y_position + 10, x_offset)  # First line below
                    draw_ledger_lines(canvas, y_position + 20, x_offset)  # Second line below
            elif 'F3' in normalized_note or "F#3" in normalized_note or "F♭3" in normalized_note:
                    draw_ledger_lines(canvas, y_position, x_offset)
                    draw_ledger_lines(canvas, y_position - 10, x_offset)
                    draw_ledger_lines(canvas, y_position - 20, x_offset)
            elif 'G3' in normalized_note or "G#3" in normalized_note or "G♭3" in normalized_note:
                    draw_ledger_lines(canvas, y_position - 5, x_offset)
                    draw_ledger_lines(canvas, y_position - 15, x_offset)

            # Move the x position for the next note
            x_offset += 30  # Space between notes

            # Wrap to the next staff if the x_offset exceeds the staff width
            if x_offset > staff_width - 20:
                x_offset = 50  # Reset x position for new staff
                current_staff += 1  # Move to the next staff
        else:
            canvas.create_text(x_offset, 50, text="x", font=('Arial', 16), fill="red")
            x_offset += 30  # Space between notes

def copy_to_clipboard(event=None):
    # Copy the selected text to the clipboard
    notes_entry.clipboard_clear()
    try:
        notes_entry.clipboard_append(notes_entry.get("sel.first", "sel.last"))
    except tk.TclError:
        pass  # Handle the case where no text is selected

def show_context_menu(event):
    # Display the context menu at the mouse pointer position
    context_menu.post(event.x_root, event.y_root)

# Create the context menu
context_menu = tk.Menu(notes_frame, tearoff=0)
context_menu.add_command(label="Copy", command=copy_to_clipboard)

# Bind right-click event to show the context menu
notes_entry.bind("<Button-3>", show_context_menu)

# Allow copying with Ctrl+C
notes_entry.bind("<Control-c>", copy_to_clipboard)

# Buttons
tk.Button(root, text="Transpose", command=display_transposed_notes).pack(pady=5)
tk.Button(root, text="Save Transposed Notes", command=save_notes).pack(pady=(5, 20))

root.mainloop()
