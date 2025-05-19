import re

# Read the characters.py file
with open('characters.py', 'r') as f:
    content = f.read()

# Replace all portrait paths
updated_content = re.sub(r'"Portrait": "/resources/Portraits/', '"Portrait": "/portraits/', content)

# Write the updated content back to the file
with open('characters.py', 'w') as f:
    f.write(updated_content)

print("Portrait paths updated successfully!")
