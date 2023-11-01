import os

folder = "output/pdf_images/Vol 2 Part 2"
find = "5e0b1c7e-aad4-42b6-bc76-c75bc41094f1"
replace = "Alford-Vol-2-Part-2"

# List all files in the directory
for filename in os.listdir(folder):
    # Filter the files you want to rename (e.g., you can use conditional statements)
    if find in filename:
        # Define the new file name (you can customize this based on your requirements)
        new_name = filename.replace(find, replace)

        # Create the full paths to the old and new file names
        old_file_path = os.path.join(folder, filename)
        new_file_path = os.path.join(folder, new_name)

        # Rename the file
        os.rename(old_file_path, new_file_path)
        print(f'Renamed: {filename} to {new_name}')