import shlex
import subprocess


# Starting FastAPI application
cmd_api = "uvicorn app.main:app --host 0.0.0.0 --port 1706 --reload --reload-dir ./app --reload-dir ./configs --reload-dir ./models --reload-dir ./tests"
command_apis = shlex.split(cmd_api)

# run procress
api = subprocess.Popen(command_apis, universal_newlines=True)
api.communicate()

