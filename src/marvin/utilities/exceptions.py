class PrefectNotInstalledError(ImportError):
    """Raised when Prefect is not installed"""

    def __init__(self, message=None):
        instructions = (
            "Prefect is not installed. You can install it with `pip install prefect`"
            " or `pip install 'marvin[framework]'`."
        )
        if message is not None:
            super().__init__(f"{message} {instructions}")
        else:
            super().__init__(instructions)
