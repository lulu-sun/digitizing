import os

folder = "extraction/output/pdf_images/vol-1-part-1"
find = "32d4e256-aadb-4bc8-b5ca-b7390a05c42d"
replace = "Alford-Vol-1-Part-1"

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