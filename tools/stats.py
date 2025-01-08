from json import dumps
import os
folders = -1
files_ = 0
python_files = 0
line = {}
file_ = {}

d = os.walk("/Users/hugo/Documents/Code/BitBot")
for path, folder, files in list(d):
    for blacklist in ['.vscode', '.git', '__pycache__', 'venv']:
        if blacklist in path:
            break
    
    else:
        folders += 1
        files_ += len(files)
        for file in files:
            try:
                content = open(f"{path}/{file}").read()
                type =  "." + file.split('.')[-1]
                if not type in line:
                    line[type] = 1
                
                if not type in file_:
                    file_[type] = 0

                file_[type] += 1
                line[type] += content.count('\n')
            
            except:
                continue

print("folders:", folders, ' files:', files_, "\nlines:", dumps(line, indent = 4), '\nfile types:', dumps(file_, indent = 4))