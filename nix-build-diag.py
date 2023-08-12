import os
import requests
import socket

def extract_imports(file_path):
    imports = []
    inactives = []
    stripper = 0 
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip().startswith('imports'):
                stripper = 1
            elif stripper and line.strip().strip('.').startswith('/'):
                line = line.strip().lstrip('[/.').rstrip('];')
                for entry in line.split():
                    imports.append(rename_folders(entry))
            elif stripper and line.strip().strip('.').startswith('#'):
                line = line.strip().lstrip('[#/.').rstrip('];')
                for entry in line.split():
                    imports.append(rename_folders(entry))
                    inactives.append(rename_folders(entry))
            elif line.strip().endswith('];'):
                stripper = 0
            
    return imports, inactives

def process_folder(folder_path):
    imports_data = []
    inactives_data = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.nix'):
                file_path = os.path.join(root, file)
                imports, inactives = extract_imports(file_path)
                if imports:
                    imports_data.append([rename_default_nix(file, file_path)]+ imports)
                if inactives:
                    inactives_data.extend(inactives)
    
    return imports_data, inactives_data

def rename_default_nix(import_name, path):
    if import_name == 'default.nix' and not os.path.basename(os.path.dirname(path)) == socket.gethostname():
        import_name = os.path.basename(os.path.dirname(path))+'/'+import_name
    elif import_name == 'default.nix' and os.path.basename(os.path.dirname(path)) == socket.gethostname():
        import_name = 'host/default.nix'
    
    return import_name        

def rename_folders(import_name):
    if not import_name.endswith('.nix'):
        import_name = import_name +'/default.nix'
    
    return import_name

def inactives_recursive(imports_data, inactives_data):
    updated_inactives_data = []
    for entry in imports_data:
        parent_value = entry[0]
        child_values = entry[1:]
        if parent_value in inactives_data:
            updated_inactives_data.extend(child_values)
    
    return updated_inactives_data

def generate_diagram_content(imports_data, inactives_data):
    diagram_content = ['blockdiag{\n']
    class_content = ['class inactives [color = "#850d28", style = dotted];']
    diagram_content.extend(class_content)
    for entry in imports_data:
        parent_value = entry[0]
        child_values = entry[1:]

        for value in child_values:
            diagram_content.append(f'"{parent_value}" -> "{value}";')
    
    for entry in inactives_data:
        diagram_content.append(f'"{entry}" [class = "inactives"];')
    diagram_content.append('}')
    
    return '\n'.join(diagram_content)

    
def save_diagram(diagram_content, output_path):
    response = requests.post('https://kroki.io/blockdiag/png', data=diagram_content)

    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)
    else: 
        print(response.status_code)

 


folder_path = os.path.expanduser('~/.config/nixos')
output_path = os.path.join(folder_path, 'nix_imports.png')
imports_data, inactives_data = process_folder(folder_path)

inactives_data.extend(inactives_recursive(imports_data, inactives_data)) 
diagram_content = generate_diagram_content(imports_data, inactives_data)
save_diagram(diagram_content, output_path)
