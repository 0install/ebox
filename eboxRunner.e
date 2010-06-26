println("E initialised")

def makeTraceln := <unsafe:org.erights.e.elib.debug.makeTraceln>
def makeELoader := <elang:interp.ELoaderAuthor>(makeTraceln)

def [json] := interp.getArgs()
println(json)

def jsonSurgeon := <elib:serial.deJSONKit>.makeSurgeon()
def launchData := jsonSurgeon.unserialize(json)
def [ => locations, => dependencies, => args, => main_uri, => main ] := launchData
println(launchData)

# URI -> (promise, resolver)
def loaders := [].asMap().diverge()
for uri => path in locations {
	loaders[uri] := Ref.promise()
}

for uri => deps in dependencies {
	def loader
	def envExtras := ["this__uriGetter" => loader].diverge()
	for [name, dep_iface] in deps {
		envExtras[`${name}__uriGetter`] := loaders[dep_iface][0]
	}
	def rx`.*/(@{leaf}[^/]+)` := uri
	traceln(`new loader $leaf from $uri with $envExtras`)
	bind loader := makeELoader(<file:/>[locations[uri]], envExtras.snapshot(), `$leaf$$`)
	loaders[uri][1].resolve(loader)
}

loaders[main_uri][0].getWithBase(main, safeScope)
