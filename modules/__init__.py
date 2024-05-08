import os
import importlib


def find_python_files(directory):
    """
    Recursively find all Python (.py) files in the subdirectories of the specified directory,
    excluding the top-level directory itself. Returns relative paths from the starting directory.

    :param directory: Path to the directory to search for Python files
    :return: A list of relative paths to Python files
    """
    python_files = []
    for root, dirs, files in os.walk(directory):
        if root == directory:  # Skip files in the top-level directory
            continue
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                # Create a relative path from the starting directory to the file
                relative_path = os.path.relpath(os.path.join(root, file), directory)
                python_files.append(relative_path.replace("\\", "/"))
    return python_files


# Get all files.
views = find_python_files(os.path.dirname(os.path.abspath(__file__)))

# Import all files from modules folder.
for view in views:
    view_path = (
        os.path.dirname(os.path.realpath(__file__)).replace("\\", "/").split("/")[-1]
        + "."
        + view[:-3].replace("/", ".")
    )
    importlib.import_module(view_path)
    print("App imported " + view + " successfully.")
