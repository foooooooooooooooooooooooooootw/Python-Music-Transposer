import tkinter as tk
from tkinter import messagebox, filedialog
import time

# Transpose mapping and chromatic scale
chromatic_scale = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
flat_to_sharp_map = {
    'C♭': 'B', 'D♭': 'C#', 'E♭': 'D#', 'F♭': 'E', 'G♭': 'F#', 'A♭': 'G#', 'B♭': 'A#'
}

# Mapping instrument names to their transpose values
instrument_transpose_map = {
    'B♭': 2,
    'E♭': -3,
    'F': 7
}

def transpose(note, shift):
    normalized_note = flat_to_sharp_map.get(note, note)
    index = chromatic_scale.index(normalized_note) if normalized_note in chromatic_scale else -1
    
    if index == -1:
        return note
    
    new_index = (index + shift) % 12
    return chromatic_scale[new_index]

def normalize_input(note):
    return note.replace('b', '♭').upper()

def transpose_notes():
    notes_input = notes_entry.get("1.0", tk.END).strip().split()
    instrument = instrument_var.get()
    transpose_value = instrument_transpose_map[instrument]
    
    normalized_input = [normalize_input(note) for note in notes_input]
    valid_notes = chromatic_scale + list(flat_to_sharp_map.keys())
    
    invalid_notes = [note for note in normalized_input if note not in valid_notes]
    if invalid_notes:
        messagebox.showerror("Invalid Notes", f"Invalid notes entered: {', '.join(invalid_notes)}.")
        return

    shift = -transpose_value if concert_var.get() else transpose_value
    transposed_notes = [transpose(note, shift) for note in normalized_input]

    output_entry.config(state='normal')
    output_entry.delete("1.0", tk.END)
    output_entry.insert("1.0", ' '.join(transposed_notes))
    output_entry.config(state='disabled')
    
    update_instrument_labels()

def update_instrument_labels():
    if concert_var.get():
        input_label_var.set(instrument_var.get())
        output_label_var.set("C")
    else:
        input_label_var.set("C")
        output_label_var.set(instrument_var.get())

def save_notes():
    if not output_entry.get("1.0", tk.END).strip():
        messagebox.showwarning("Warning", "No transposed notes to save.")
        return
    
    notes = output_entry.get("1.0", tk.END).strip()
    input_notes = notes_entry.get("1.0", tk.END).strip()
    
    # Generate the default filename
    default_filename = f"{instrument_var.get()}-{int(time.time())}.txt"
    
    # Open save file dialog with the default filename
    filename = filedialog.asksaveasfilename(defaultextension=".txt",
        initialfile=default_filename,
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    
    if filename:
        with open(filename, 'w', encoding='utf-8') as file:  # Specify UTF-8 encoding
            if save_both_var.get():  # Check if the checkbox is checked
                file.write(f"{input_label_var.get()} Instrument Input\n")
                file.write(input_notes + "\n\n")
                file.write(f"{output_label_var.get()} Instrument Output\n")
                file.write(notes + "\n")
            else:
                file.write(notes)
        
        messagebox.showinfo("Success", f"Transposed notes saved as {filename}")

# Tkinter GUI setup
root = tk.Tk()
root.title("Python Music Transposer")

# Frame for input and output
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# Input for notes
tk.Label(frame, text="Enter Notes (C, D, E, F, G, A, B, ♭, #):").grid(row=0, column=0, sticky='w')
notes_entry = tk.Text(frame, width=30, height=20, font=('Arial', 14))
notes_entry.grid(row=1, column=0, padx=5, pady=5)

# Output for transposed notes
tk.Label(frame, text="Transposed Notes:").grid(row=0, column=1, sticky='w')
output_entry = tk.Text(frame, width=30, height=20, fg="blue", font=('Arial', 14), state='disabled')
output_entry.grid(row=1, column=1, padx=5, pady=5)

# Labels for displaying instrument names
input_label_var = tk.StringVar(value="C")
output_label_var = tk.StringVar(value="B♭")
tk.Label(frame, textvariable=input_label_var).grid(row=2, column=0)
tk.Label(frame, textvariable=output_label_var).grid(row=2, column=1)

# Instrument selection for transpose
tk.Label(root, text="Select Instrument:").pack(pady=(10, 0))
instrument_var = tk.StringVar(value='B♭')
tk.OptionMenu(root, instrument_var, *instrument_transpose_map.keys(), command=lambda _: update_instrument_labels()).pack(pady=5)

concert_var = tk.BooleanVar()
concert_checkbox = tk.Checkbutton(root, text="Convert To/From Concert Pitch", variable=concert_var, command=update_instrument_labels)
concert_checkbox.pack(pady=5)

# New checkbox for saving both input and output
save_both_var = tk.BooleanVar()
save_both_checkbox = tk.Checkbutton(root, text="Save both input and output notes", variable=save_both_var)
save_both_checkbox.pack(pady=5)

# Buttons
tk.Button(root, text="Transpose", command=transpose_notes).pack(pady=5)
root.bind('<Return>', lambda event: transpose_notes())
tk.Button(root, text="Save Transposed Notes", command=save_notes).pack(pady=(5, 20))

root.mainloop()
