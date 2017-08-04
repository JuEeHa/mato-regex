import compiler

class Thread:
	def __init__(self, instruction, *, register = None):
		self.instruction = instruction
		self.register = register

def run_vm(ir, text):
	index = 0
	threads = [Thread(ir)]

	while len(threads) > 0:
		new_threads = []
		all_blocking = True

		# Run all threads that aren't blocking on input
		for thread in threads:
			# Register value None means we aren't blocking on input
			if thread.register == None:
				all_blocking = False

				if thread.instruction == None:
					# We should've reached the end of text. If we have, we've found a match. If not, the thread should die
					if not index < len(text):
						return True

				elif type(thread.instruction) == compiler.Split:
					new_threads.append(Thread(thread.instruction.first))
					new_threads.append(Thread(thread.instruction.second))

				elif type(thread.instruction) == compiler.Match or type(thread.instruction) == compiler.Any:
					# Setting register value to 0 means we're matching against the first character and blocking on input
					new_threads.append(Thread(thread.instruction, register = 0))

				else:
					assert False # Unreachable

			else:
				new_threads.append(thread)

		threads = new_threads

		# All threads are blocking. We should consume one character of input and check the matches
		if all_blocking:
			new_threads = []

			# Only bother to run threads if there is text to match against
			if index < len(text):
				for thread in threads:
					if type(thread.instruction) == compiler.Match:
						# Match character against input
						# If it matches, add to the new threads and update register / instruction
						# Otherwise, drop the thread
						if thread.instruction.text[thread.register] == text[index]:
							if thread.register + 1 < len(thread.instruction.text):
								# We'll still be inside this match instruction, update register
								new_threads.append(Thread(thread.instruction, register = thread.register + 1))
							else:
								# We'll move to the next instruction, update instruction
								new_threads.append(Thread(thread.instruction.end))

					elif type(thread.instruction) == compiler.Any:
						# Always succeed (assuming there's input, naturally)
						# Add next instruction to the new threads
						new_threads.append(Thread(thread.instruction.end))

				index += 1

			threads = new_threads

	# We didn't get a match
	return False

def match(regex, text):
	return run_vm(compiler.compile(regex), text)
