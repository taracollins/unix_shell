import os, getpass, socket, sys, subprocess, multiprocessing, threading
from style import colour

# A lock is created here. It will be used to ensure that no two processes write to a file at the
# same time
lock = threading.Lock()

# Used to format the readme file when it is printed by the help function. Each of these commands will appear in bold
# with the use of ascii characters
command_list = ["cd", "dir", "clr", "help", "pause", "echo", "environ", "quit", ">", ">>"]

# start_dir is used to store the location that myshell.py  is ran from. This will be used for the readme later. 
# As stated in the readme, if the files are not in the same folder then the help function will throw an errror as 
# seen in the do_help() function below 
start_dir = os.getcwd()

# to_file is a dictionary that will be used to determine how a file is outputted to. Similarly,
# commands is used to store the internal command list. The keys are strings of the internal commands.
# the values are the function names that are used to call the internal commands
to_file = {">" : "w", ">>" : "a+"}

# This creates the command-line prompt. It takes the username as USR, the name of the machine as HOST and 
# the current working diretory as CWD and uses input() to take user input
def prompt(USR, HOST, PWD):
	line = input(USR + " in " + HOST + " at " + PWD + " --> ")
	return line

# This function is used to check whether the the output will go to terminal or to a file. It will be
# used a lot in the functions below
def checker(args):
	if ">" in args or ">>" in args:
		return True
	return False

# All functions will acquire their output before determining where the output is going
# If it is determined that the output is to go to a file instead of to the terminal screen, this
# function will handle that. args is the list of command-line arguments that were entered by
# the user. output is what will be outputted to the file which is determined prior to calling
# this function
def outputter(args, output):
	# If > is the output symbol then the file will be truncated if
	if ">" in args:
		filename, output_type = args[args.index(">") + 1], to_file[">"]
	else:
		filename, output_type = args[args.index(">>") + 1], to_file[">>"]
	with open(filename, output_type) as f:
		lock.acquire()
		f.write(output + "\n")
		lock.release()

# This function handles the launching of external programs and any other system utilies
def launch_external(args):
	# First check if the output is going to a file or to the terminal. Forking and calling
	# execvp() is the best way to execute an external program or a system utility. However,
	# this will only execute the program and will not give the shell access to the program output
	# This is why subprocess is to direct the output to a file
	if checker(args):
		try:
			# If we're outputting to a file, we create a subprocess that will run in the background
			# subprocess.check_output() will run with the arguments given and return a byte string
			# This checkes whether there is an & and whether it needs to run in the background or not
			# This will change what is put in the check_output() function
			if "&" in args:
				output = subprocess.check_output(args[:-3])
			else:
				output = subprocess.check_output(args[:-2])
			# output.decode() is used to decode the btye string that is stored in output. This will 
			# decode it to a string that will be stored in output_dec
			output_dec = output.decode('ascii')
			# This will output to a file as seen in the function above
			outputter(args, "".join(output_dec))
		except Exception as e:
			print("myshell >>> an error occured while processing command. Command or file does not exist")
	# Otherwise, the output is going to the terminal so execvp() is called to run the external program.
	else:
		# We create a child process using os.fork()
		pid = os.fork()
		# Check if that if it is a child process. A child process will have no PID (process ID) and thus will not
		# have a PID created than 0.
		if pid > 0:
			# Obtains the status of any child process, and waits for it to finish executing
			wpid = os.waitpid(pid,0)
		else:
			try:
				# os.execvp() will run the external program, args[0] is the program name and the rest
				# are the program arguments
				os.execvp(args[0], args)
			# If this point is reached then the command does not exist internally or externally,
			# and thus the error is reported
			except Exception as e:
				print("myshell >>> command not found: " + colour.bold + args[0] + colour.end)

# This function runs when myshell.py is launched with arguments following it on the command-line
def batchfile(args):
	try:
		# Opens the batch file and calls run to execute each command
		for line in open(args, "r"):
			run(line.split())
	except FileNotFoundError:
		# If an error occurs then tell the user that the file cannot be ran
		print("myshell >>> cannot access batchfile, no such file: " + colour.bold + args + colour.end)

# Uses ascii characters from the colour class imported to clear the screen. Takes args in the case
# that it is ran as a background process. args will be ignored in all other cases
def clear(args = None):
	print(colour.clr, end = '')

# Tells the shell to wait for user input, system is used to display the "Press enter to continue" prompt
# Takes args = None in the case that it is ran as a background process. Otherwise, pause
# will ignore any given arguments
def pause(args = None):
	try:
		os.system('read -p "Press enter to continue..."')
	except Exception:
		print("myshell >>> could not pause operations")

# Takes userInput from command-line arguments. userInput will be taken as a list and joined
# back together to eliminate any unnecessary whitespace. Default argument is None so that it may
# be ran as a background process
def echo(userInput = None):
	try:
		# Checks if there is input or if it'll be ran as a background process
		if userInput:
			# Checks if the output is going to a file
			if checker(userInput):
				outputter(userInput, " ".join(userInput[0:-2]))
			# Otherwise print text joined together in terminal
			else:
				print(" ".join(userInput))
	except Exception as e:
		print("myshell >>> an error occurred:" + e)

# This will print out the contents of the current directory if a directory is not given, this
# the args is optional. Otherwise it will go to the directory being requested so that it may
# list the contents of it
def directory(args = None):
	# Saves the location of the current directory, to be returned to later
	path = os.getcwd()
	try:
		# Change to requested directory, and acquire the output
		if args and not checker(args):
			os.chdir(args[0])
		output = "\n".join(os.listdir("."))
		# If it is not going to a file then output it to the terminal
		if not checker(args):
			print(output)
		# It is going to a file, call the function to output it
		else:
			outputter(args, output)
		# return to original directory
		os.chdir(path)
	except FileNotFoundError:
		print("myshell >>> no such file or directory: " + colour.bold + args[0] + colour.end)

# Lists all the environment variables. Takes args in the case that the environ variables are
# outputted to a file instead of to terminal. This also ensures that it may be ran as a background
# process
def environ(args = None):
	# Acquire the length of the longest key in order to format the output neatly
	environ = os.environ
	length = len(max(environ.keys(), key = len))
	# Store output here so we may decide to output it to a file or to the terminal at a later stage
	output = []	
	for key in environ:
		# Use a ':' to seperate the keys from their values so it will be clear when output is printed
		output.append("{:<{}s}  :  {}".format(key, length, environ[key]))
	output = "\n".join(output)
	# Here, if there are any arguments then we know that it is going to a file
	if args:
		outputter(args, output)
	# Otherwise, it is going to be outputted to the terminal
	else:
		print(output)

# Prints the readme file which should be stored in the same folder as myshell.py as specified
def do_help(args = None):
	# This is the location of the help file. We know as start_dir was acquired before any processes
	# were ran or commands were called
	helpfile = start_dir +"/readme"
	# terminal_width is used to format the output
	terminal_width = os.get_terminal_size()[0]
	try:
		# Opens it in read only mode
		with open(helpfile, 'r') as f:
			# Reads the whole file into a variable. readlines() is used as the readme file
			# is not very large, otherwise a loop would be used to read each line one at a time
			file = f.readlines()
			# check if it is going to terminal or to a file
			if args:
				if checker(args):
					outputter(args, "\n".join(file))
			else:
				# Use the clear function to clear the screen so that the help file will be 
				# displayed more clearly
				clear()
				for line in range(len(file)):
					word = file[line]
					# Prints the headers in bold and seperates them with '-'s based on the size
					# of the terminal
					if word.split() and word.split()[0].isupper() and word.split()[0].isalpha():
						print("-" * terminal_width)
						print(colour.bold + word + colour.end, end = '')
					# Prints the commands in bold, makes the file read more clearly
					elif word.split() and word.split()[0] in command_list:
						print(colour.bold + word + colour.end, end = '')
					# Otherwise, it is a normal line, print regularly
					else:
						print(word, end = '')
					# Request that the user pressed enter every 20 lines, similar to a more filter
					if line % 20 == 0:
						input(colour.invert + colour.black + "Press enter to continue" + colour.end)

	except FileNotFoundError:
		print("myshell >>> readme must be in the same directory as myshell.py")			

# Allows the user to return to previous directories
def prevdirectory(args = None):
	try:
		os.chdir("/".join(os.getcwd().split("/")[:-1]))
	# Prfevents the user from trying to return to parent directories that do not exist
	except FileNotFoundError:
		print("myshell >>> directory does not exist")

def cd(args):
	try:
		# If no arg is provided then we just report the folder that we are currently in
		if not len(args):
			#home_dir = os.path.expanduser("~") could be used to return to the home directory
			print("Currently in " + os.getcwd())
		else:
			# Otherwise, change to the folder that the user requests and update the environ variable
			# for PWD
			os.chdir(args[0])
			os.environ["PWD"] = os.getcwd()
	except FileNotFoundError:
		print("myshell >>> no such file or directory " + colour.bold + args[0] + colour.end)

# Calls upon the system to exit the shell
def quit(args = None):
	print("myshell >>> quitting...")
	sys.exit(0)

# Executes processes in the background
def backgroundprocess(command, argus):
	try:
		# If there are arguments required, create the subprocess with arguments supplied
		if argus:
			multiprocessing.Process(target = command, args = (argus,)).start()
		# Otherwise call the subprocess without any arguments
		else:
			multiprocessing.Process(target = command, args = ()).start()	
	except:
		print("myshell >>> an error occurred: could not execute background process")

# This function determines what command has been called, whether the function for it exists,
# whether the process is to be ran as a background process or whether it is an external command.
def run(args):
	commands = { "cd" : cd,
				"dir" : directory,
				"batchfile" : batchfile,
				"environ" : environ,
				"echo" : echo,	
				"help" : do_help,
				"quit"	: quit,
				"clr" : clear,
				"pause" : pause,
				".." : prevdirectory	
				}
	try:
		# Nothing was provided on the command-line. Wait for input
		if len(args) == 0:
			pass
		# Check if it is an internal command
		elif args[0] in commands:
			# If it is check if it is to be ran as a background process
			if args[-1] == "&":
				backgroundprocess(commands[args[0]],args[1:-1])
			# If it is not, call the function to run the process
			else:
				commands[args[0]](args[1:])
		# It is not an interal command, check if the program can be ran through external system utilities
		else:
			launch_external(args)
	except EOFError as e:
		print("")

def main():
	# Set environ variable for the shell
	os.environ["shell"] = os.path.realpath(__file__)
	shell = os.getcwd() + "/myshell"
	# Variable to hold what directory myshell.py is in. Is used to open readme 
	myshell_file = os.getcwd() + "/" + sys.argv[0]
	# If there is anything else present on the command-line upon invocation then it must be a 
	# batchfile. Try to run
	if len(sys.argv) > 1:
		batchfile(sys.argv[-1])
	else:
		# Otherwise, start an infinite loop that will run until the user calls the quit command
		while True:
			# Current user
			USR = getpass.getuser()
			# Current machine/host
			HOST = socket.gethostname()
			# Current directory
			PWD = os.getcwd()

			# Command-line prompt
			line = prompt(USR, HOST, PWD)
			# Command-line arguments to call commands
			args = line.split()
			# Executes commands
			run(args)

if __name__ == '__main__':
	main()
