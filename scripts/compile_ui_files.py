import os
import subprocess

def compile_ui_files():
    ui_dir     = r"src\ui\forms"
    output_dir = r"src\ui\compiled"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for file in os.listdir(ui_dir):
        if file.endswith('.ui'):
            ui_file = os.path.join(ui_dir, file)
            py_file = os.path.join(output_dir, f"ui_{file[:-3]}.py")
            
            cmd = f"pyside6-uic {ui_file} -o {py_file}"
            subprocess.run(cmd, shell=True)
            print(f"Compiled: {file} -> ui_{file[:-3]}.py")

if __name__ == "__main__":
    compile_ui_files()