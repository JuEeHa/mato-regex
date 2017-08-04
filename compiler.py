from collections import namedtuple
import parser

Match = namedtuple('Match', ['text', 'end'])
Any = namedtuple('Any', 'end')
Beginning = namedtuple('Beginning', 'end')
End = namedtuple('End', 'end')

class Split:
	def __init__(self, first, second):
		self.first = first
		self.second = second

	def __repr__(self):
		return 'Split(first = %s, second = %s)' % (repr(self.first), repr(self.second))

def compile_parsed(parsed):
	def sequence(parsed, *, end):
		# Build the sequence in reverse order (since everything has an "end" field marking where to move next)
		current = end
		for element in reversed(parsed):
			current = fragment(element, end = current)
		return current

	def fragment(parsed, *, end):
		if type(parsed) == list:
			if len(parsed) == 0:
				return end

			elif len(parsed) == 1:
				parsed, = parsed

			else:
				return sequence(parsed, end = end)

		if type(parsed) == str:
			return Match(text = parsed, end = end)

		elif type(parsed) == parser.Bar:
			left = fragment(parsed.left, end = end)
			right = fragment(parsed.right, end = end)
			return Split(left, right)

		elif type(parsed) == parser.Star:
			# Order is important here
			# We have split pointing to inner, and inner pointing to split
			# Since * allows zero repetitions, we should start with split
			split = Split(end, None)
			inner = fragment(parsed.inner, end = split)
			split.second = inner
			return split

		elif type(parsed) == parser.Dot:
			return Any(end = end)

		elif type(parsed) == parser.Caret:
			return Beginning(end = end)

		elif type(parsed) == parser.Dollar:
			return End(end = end)

		else:
			assert False # unreanchable

	return fragment(parsed, end = None)

def compile(text):
	return compile_parsed(parser.parse(text))
