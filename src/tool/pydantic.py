from colorama import Fore
from pydantic import ValidationError


def print_validation_error(error_exc: ValidationError):
    errors = error_exc.errors()
    print(Fore.YELLOW + "Validation error in ExtractSchema:")

    for error in errors:
        location = " -> ".join(str(loc) for loc in error["loc"])
        input_value = error.get("input", "N/A")
        error_type = error["type"]
        error_msg = error["msg"]

        print(Fore.YELLOW + f"  Field: {location}")
        print(Fore.YELLOW + f"  Value: {input_value}")
        print(Fore.YELLOW + f"  Error: {error_type} - {error_msg}")