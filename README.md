# The caching DNS-server

The program binds a given host and 53 port, so user should 
have administrator privillages. The program also nesessary 
takes a forwarder address and port because it's cache is 
empty in the moment after launch.

Server receives clients requests and looks for requested 
names in it's cache. If there is a record in the cache and 
this record is actual (a records TTL is not exceeded), 
server sends a response to client. In the opposit case 
server sends this request to it's forwarder and takes the 
forwarder information to answer to the client and to write 
it to cache.

Server keeps records in it's cache by domain names. It also 
keeps a response package, a time of this record making and 
it's TTL for each of record. Server changes information about 
deprecated records.

By default cache record TTL is set to 15 minutes. It can be 
changed in configurations of the file cache_record.py

Server can be stoped any time during it works by typing a
special command: "close". Closing command can be changed in
configurations of a main file.

For a help message showing use --help or -h argument.
