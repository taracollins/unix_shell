# My Shell

myshell.py is a simple shell that takes command line arguments. Run using Python3. Keep README.md in the same folder as myshell.py in order to be able to display this manual in the terminal

## SYNOPSIS

__myshell.py [OPTION] [ARG] [FILE]__    

## DESCRIPTION
myshell.py supports a collection of internal commands. If a command is entered in to the command line that is not recognised as an internal command, myshell.py will search the system utilities for the given command and run it as a child process. All arguments and parameters must be seperated by whitespace. This includes a space or a tab. myshell.py may be ran with a batchfile containing commands on the command line. Once all commands in the batchfile have been executed, myshell.py will exit

## ARGUMENT LIST PROCESSING

#### __cd [DIRECTORY]__
changes the current directory to DIRECTORY. If DIRECTORY is not given then the value of the current directory is reported. Any command-line arguments following DIRECTORY will be ignored. If DIRECTORY does not exist, it will be reported. To return to previous directory, input .. to the command-line

#### __clr__
clears the terminal screen. Does not take parameters, any following command-line arguments will be ignored

#### __dir [DIRECTORY] __
lists all the contents of DIRECTORY. If DIRECTORY is not supplied, the contents of the currently directory will be listed. If FILE is provided, ouput will be directed there, otherwise it will be displayed in the terminal

#### __environ __
reports the list of environments along with their value. Ignores any following command-line arguments. Seperated keys and values with :

#### __echo [TEXT]__
displays TEXT in the terminal or to an output file if directed. TEXT will be formatted to reduce multiple spaces and/or tabs to a single space

#### __help__
displays the user manual in the terminal. 20 lines are displayed at a time. User must press the spacebar to continue to view the next 20 lines. Function will exit once the full manual has been displayed

#### __pause__
pauses all operations. Operations will be resumed when "enter" button is pressed. Any following parameters will be ignored.

#### __quit__
exits the shell. Ignores any following command-line arguments

## INPUT / OUTPUT REDIRECTION

Output from a program or from an internal command may be outputted to a file. All parameters must be presented on the command-line. If a redirection symbol is not provided, output will be not be redirected to a file and instead it will be directed to the terminal. dir, environ, echo and help support output redirection

#### __Redirection symbols__

__>__

If the file following this symbol exists, the file will be overwritten by the program output. If the file does not exist, it will be created with the content being the program output

__>>__

If the file following this symbol exists then the program output is appended to it. If the file does not exist, it will be created with the content being the program output

## __Invocation__
__[COMMAND] [ARGS] [SYMBOL] [FILE]__
        
Executes COMMAND with optional ARGS. COMMAND may refer to either interal commands of the shell or an external program. SYMBOL determines how the output will be treated. FILE determined location of the output. 

#### __BACKGROUND PROCESSES__

Any of the internal or external commands may be run as a background process. This means that the user may not intervene with the process while it is running

#### __[COMMAND] [&]__
& is what tells the shell to run this command in the background
