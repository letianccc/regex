#
#
# 正则表达式引擎
#
# 		 Regular Expression. Here is a brief description of the regular expression grammar:
#
# 			1)  Charset:
# 				    a, [a-z], [^a-z]
#
# 			2)  Escaped characters:
# 					\r: the CR character
# 					\n: the LF character
# 					\t: the tab character
# 				    \s: spacing characters (including space, \r, \n, \t)
# 			    	\S: non-spacing characters
# 					\d: [0-9]
# 					\D: [^0-9]
# 					\w: [a-zA-Z0-9_]
# 					\W: [^a-zA-Z0-9_]
# 					\\, \/, \(, \), \+, \*, \?, \{, \}, \[, \]: represents itself
# 			    Escaped characters in charset defined in a square bracket:
# 					\r: the CR character
# 					\n: the LF character
# 					\t: the tab character
# 					\-, \[, \], \\, \/, \^: represents itself
# 			3)  Loops:
# 				regex{3}: repeats 3 times
# 				regex{3,}: repeats 3 or more times
# 				regex{1,3}: repeats 1 to 3 times
# 				regex?: repeats 0 or 1 times
# 			    regex*: repeats 0 or more times
# 				regex+: repeats 1 or more times
# 			4)	(regex): No capturing, just change the operators' association
#

