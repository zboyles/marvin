import typer
import subprocess
import os 
import importlib
from .scripts.get_settings import get_settings

app = typer.Typer()


@app.command()
def runserver():
    config = get_settings()
    print(config)
    # subprocess.run(["uvicorn", "marvin.api.main:app", "--reload"])

if __name__ == "__main__":
    app()