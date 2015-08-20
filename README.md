# cef binding generator for servo

Do NOT rely on this for building a CEF library. This repository
will only contain up-to-date header files for use with either
updating Servo's CEF bindings or compiling a native browser chrome.
Instead, use a build from http://cefbuilds.com (thanks Adobe!)

To update bindings:
* git remote add upstream https://bitbucket.org/chromiumembedded/cef.git
* git fetch upstream
* git rebase upstream/master
* merge conflicts
* mkdir -p libcef_dll/rust/test
* run tools/translator.sh
* cp libcef_dll/rust/*.rs /path/to/servo-git/ports/cef/interfaces
* cd /path/to/servo-git/ports/cef
* ./regen_interface_mod_rs.sh
* cp interfaces_mod.rs interfaces/mod.rs
* commit
