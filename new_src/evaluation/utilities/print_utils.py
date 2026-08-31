
import sys

def clear_above_lines(lines: int = 2) -> None:
    """
    Clear n lines above the current line.
    """
    for _ in range(lines):
        # Move up one line and clear it
        sys.stdout.write('\033[F\033[K') 

def update_lines(lines: list[str]) -> None:
    """
    Update the len(lines) upper lines in the terminal.
    """

    # Clear the last n lines printed above
    clear_above_lines(len(lines))
    
    # Print the lines
    for line in lines:
        print(line)