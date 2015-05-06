# cef binding generator for servo

Do NOT rely on this for building a CEF library.
Instead, use https://github.com/pcwalton/chromium-embedded-framework
or a build from cefbuilds.com

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
