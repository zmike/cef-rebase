# Servo's fork of the Chromium Embedding Framework

Installing the Servo CEF fork is much simpler than installing upstream CEF,
because it is more loosely coupled to the browser engine.

You'll need the `depot_tools` in your path somewhere. You can set this up
with:

    $ git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
    $ export PATH=$PATH:/path/to/depot_tools

Then, all you need to do is the following:

    $ cd cef3
    $ ./cef_create_projects.sh
    $ cd tools
    $ ./make_distrib.sh

You will now have a `libcef_dll` in
`binary_distrib/cef_binary_3.0.0_${YOUR_PLATFORM}/libcef_dll` and headers in
`binary_distrib/cef_binary_3.0.0_${YOUR_PLATFORM}/include`. When building a
project that embeds Servo:

 * Pass `-Ibinary_distrib/cef_binary_3.0.0_${YOUR_PLATFORM}` in your
   `CPPFLAGS` (note: not the `include` subdirectory).
 
 * Build and statically link against all source files in
   `binary_distrib/cef_binary_3.0.0_${YOUR_PLATFORM}/libcef_dll`. This allows
   your app to use nice C++ wrappers around the low-level C APIs.
 
 * Dynamically link against
   `${SERVO}/ports/cef/target/libembedding-${HASH}.{dylib,so}` (for a debug
   build) or
   `${SERVO}/ports/cef/target/release/libembedding-${HASH}.{dylib,so}` (for a
   release build).

Have fun!
