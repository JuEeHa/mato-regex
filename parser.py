from collections import namedtuple

class ParseError(Exception): None

Text = namedtuple('Text', 'text')
Star = namedtuple('Star', 'inner')
Bar  = namedtuple('Bar', 'left right')

def parse(text):
	def eof():
		nonlocal index, length
		return not index < length

	def read_token():
		nonlocal text, length, index

		if eof():
			raise ParseError('Unexpected end of text')

		token = text[index]
		index += 1

		if token == '\\':
			if eof():
				raise ParseError('Unexpected end of text')

			token += text[index]
			index += 1

		return token

	def peek_token():
		nonlocal text, length, index

		if eof():
			raise ParseError('Unexpected end of text')

		return text[index]

	def expression(*, subexpression = True):
		nonlocal length, index

		def pop_parsed():
			nonlocal parsed
			if len(parsed) == 0:
				raise ParseError('Unexpected empty stack')

			return parsed.pop()

		def get_last_element():
			nonlocal parsed

			element = pop_parsed()

			# Since longer strings are combined into one Text object, we have to take apart Text objects longer than one
			# In case of (foo) this won't take it apart since that'll be [Text(foo)], not just Text(foo)
			if type(element) == Text and len(element.text) > 1:
				parsed.append(Text(element.text[:-1]))
				element = Text(element.text[-1])

			return element

		def append_char(token):
			nonlocal parsed

			# \x is passed as one token, remove the escape slash
			if token[0] == '\\':
				char = token[1:]
			else:
				char = token

			if len(parsed) > 0 and type(parsed[-1]) == Text:
				previous = pop_parsed().text
				parsed.append(Text(previous + char))
			else:
				parsed.append(Text(char))

		parsed = []
		while True:
			if not subexpression and eof():
				break

			token = read_token()

			if token == ')':
				if subexpression:
					break
				else:
					raise ParseError('Unexpected ")"')

			elif token == '(':
				parsed.append(expression())

			elif token == '*':
				parsed.append(Star(get_last_element()))

			elif token == '|':
				parsed = Bar(parsed, expression(subexpression = subexpression))
				break

			else:
				append_char(token)

		return parsed

	length = len(text)
	index = 0

	return expression(subexpression = False)
