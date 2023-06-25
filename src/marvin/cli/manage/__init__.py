import typer
import subprocess
import os 

app = typer.Typer()

filename = os.path.abspath(__file__)

@app.command()
def runserver():
    subprocess.run(["uvicorn", "marvin.api.main:app", "--reload"])

if __name__ == "__main__":
    app()