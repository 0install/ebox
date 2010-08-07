#!/usr/bin/env python

version = '0.1'

import os, sys, json, shutil
from optparse import OptionParser

from zeroinstall import SafeException
from zeroinstall.injector import model, iface_cache
from zeroinstall.helpers import ensure_cached

parser = OptionParser(usage="usage: %prog [options] dir interface\n"
		"Creates a new directory 'dir' with a new instance of the given program.\n"
		"Running dir/AppRun runs the instance in an E sandbox.")
parser.add_option("", "--run", help="run the given instance", dest='apprun', metavar='APPRUN')
parser.add_option("-V", "--version", help="display version information", action='store_true')
parser.disable_interspersed_args()

(options, args) = parser.parse_args()

def _get_implementation_path(impl):
	return impl.local_path or iface_cache.iface_cache.stores.lookup_any(impl.digests)

if options.version:
	import zeroinstall
	print "ebox (zero-install) " + version
	print "Copyright (C) 2010 Thomas Leonard"
	print "This program comes with ABSOLUTELY NO WARRANTY,"
	print "to the extent permitted by law."
	print "You may redistribute copies of this program"
	print "under the terms of the GNU Lesser General Public License."
	print "For more information about these matters, see the file named COPYING."
	sys.exit(0)

def ensure_no_symlinks(path):
	# TODO: if we've got a .manifest it might be quicker to check that

	for root, dirs, files in os.walk(path):
		for item in dirs + files:
			full = os.path.join(root, item)
			if os.path.islink(full):
				# Allows getting read access to the rest of the filesystem
				raise SafeException("Package file %s is a symlink; this is not currently allowed, sorry!" % full)

my_dir = os.path.dirname(__file__)
try:
	apprun = options.apprun
	if apprun:
		# Run existing app-dir
		appdir = os.path.dirname(os.path.realpath(apprun))
		print "Running E instance", appdir
		with open(os.path.join(appdir, 'uri')) as uri_stream:
			root_uri = uri_stream.read()
		print "Selecting", root_uri
		sels = ensure_cached(root_uri)

		locations = {}
		dependencies = {}
		for uri, impl in sels.selections.items():
			locations[uri] = _get_implementation_path(impl)

			ensure_no_symlinks(locations[uri])

			my_deps = []
			for dep in impl.dependencies:
				dep_impl = sels.selections[dep.interface]
				assert not dep_impl.id.startswith('package:'), dep_impl
				for b in dep.bindings:
					if isinstance(b, model.EnvironmentBinding):
						assert b.insert == ""
						my_deps.append((b.name, dep.interface))
			dependencies[uri] = my_deps

		main = sels.selections[root_uri].attrs.get("http://erights.org/0install main", None)
		if not main:
			raise SafeException("No emain attribute on %s in %s" % (sels.selections[root_uri], root_uri))

		launch_data = {
			'locations': locations,
			'dependencies': dependencies,
			'args': args,
			'mainURI': root_uri,
			'main': main,
			'instancePath': appdir,
		}

		e_runner = os.path.join(my_dir, 'eboxRunner.e-swt')
		rune = os.environ['EBOX_RUNE']
		print "Loading E..."
		os.execv(rune, [rune, e_runner, json.dumps(launch_data)])
		assert 0
	else:
		# Create new instance
		if len(args) != 2:
			parser.print_help()
			sys.exit(1)
		appdir, uri = args
		if os.path.exists(appdir):
			raise SafeException("Instance directory '%s' already exists!" % appdir)

		uri = model.canonical_iface_uri(uri)

		# Download it now. Also checks that it's valid.
		sels = ensure_cached(uri)

		os.mkdir(appdir)
		os.mkdir(os.path.join(appdir, "config"))
		os.mkdir(os.path.join(appdir, "data"))
		os.mkdir(os.path.join(appdir, "auths"))

		with open(os.path.join(appdir, 'uri'), 'w') as uri_stream:
			uri_stream.write(uri)

		shutil.copyfile(os.path.join(my_dir, 'defaultAuths.e'), 
				 os.path.join(appdir, 'defaultAuths.e'))

		apprun_path = os.path.join(appdir, 'AppRun')
		with open(apprun_path, 'w') as apprun:
			apprun.write("#!/bin/sh\n")
			apprun.write('exec 0launch http://0install.net/tests/ebox.xml --run "$0" -- "$@"\n')

			# Make new script executable
			os.chmod(apprun_path, 0111 | os.fstat(apprun.fileno()).st_mode)

		print "Created instance directory. To run:"
		print "%s/AppRun" % appdir
except SafeException, ex:
	print >>sys.stderr, ex
	sys.exit(1)
