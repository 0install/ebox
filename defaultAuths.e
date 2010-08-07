# These authorities are added to the environment of the main E program file
# that is run. It can choose whether to pass these to other parts of the
# program or not. Comment or uncomment them as desired.

# <data> gives read and write access to the "data" subdirectory.
# The shallowReadOnly() stops it from deleting the directory itself.
# Change it to deepReadOnly if you don't want it writing anything inside
# the directory.
def <data> := <instance:data>.shallowReadOnly()

[
# Access to the standard Unix streams...

	=> stdout,
	=> stderr,
	=> stdin,
	=> print,
	=> println,

# Access to the main-loop, system properties, arguments

	=> interp,

# A source of random numbers and access to the current time.
# These allow the program to behave non-deterministically (the same
# input may produce different output):

	=> entropy,
	=> timer,

# The "data" subdirectory within the instance

	=> <data>,

# Networking using capabilities
# Allows access to any service the program author had access to, and
# the ability to gain access to new services after being given an
# capability URI (authorisation code).

	# => captp__uriGetter,
	# => introducer,
	# => identityMgr,
	# => makeSturdyRef,

# Other networking

	# => <http>,
	# => <ftp>,
	# => <gopher>,
	# => <news>,


# The powerbox grants limited access to SWT (the graphical toolkit),
# the ability to load and save files selected by the user, and the
# ability to ask for extra authority.

	=> powerbox,

# Unrestricted access to SWT (the graphical toolkit)
# e.g. opening a window without the title starting with the
# program's name

	# => <swt>

# Java

	# => <jar>,

# Threading

	# => currentVat,

# Full access to everything
# (enabling any of these allows the program to escape the sandbox)

	# => <unsafe>,
	# => <file>,
	# => makeCommand,
	# => rune,
]
