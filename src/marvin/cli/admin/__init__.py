import typer
import os 
import shutil

from pathlib import Path

# Get the absolute path of the current file
filename = Path(__file__).resolve()

# Navigate two directories back from the current file
source_path = filename.parent.parent.parent / "framework"

app = typer.Typer()

@app.command()
def startproject(no_input: bool = False):
    project_name = typer.prompt("Project Name")
    shutil.copytree(
        source_path,
        os.path.join(os.getcwd(), project_name)     
    )   

@app.command()
def startapp(no_input: bool = False):
    print('beep')
    
if __name__ == "__main__":
    app()