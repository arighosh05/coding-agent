### code

```
import os

def process_file(file_path):
    file = open(file_path, "r") 
    data = file.read()
    
    if "password" in data:
        print("Sensitive data detected!")

    os.system("rm -rf /tmp/temp_folder")  
    return data
```

### context

```
this function takes a file as input, reads the contents of the file, checks if it contains the word "password", and deletes a temporary folder. it is meant to handle basic file processing but does not have any security checks.
```


