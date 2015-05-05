# Copyright (c) 2011 The Chromium Embedded Framework Authors. All rights
# reserved. Use of this source code is governed by a BSD-style license that
# can be found in the LICENSE file.

from cef_parser import *
from date_util import *

def make_raw_rust_member_funcs(funcs, defined_names, translate_map, indent):
    result = ''
    first = True
    for func in funcs:
        comment = func.get_comment()
        if first or len(comment) > 0:
            result += '\n'+format_comment(comment,
                                          indent,
                                          translate_map,
                                          prevent_rust_doc_comment_confusion=True)
        if func.get_retval().get_type().is_result_string():
            result += indent+'// The resulting string must be freed by calling cef_string_userfree_free().\n'
        parts = func.get_raw_rust_parts()
        result += wrap_code(indent+'pub '+parts['name']+': Option<extern "C" fn('+
                            string.join(parts['args'], ', ')+') -> '+parts['retval']+'>,')
        if first:
            first = False
    return result

def make_wrapped_rust_member_funcs(funcs, defined_names, translate_map, indent):
    result = ''
    first = True
    for func in funcs:
        comment = func.get_comment()
        if first or len(comment) > 0:
            result += '\n'+format_comment(comment,
                                          indent,
                                          translate_map,
                                          prevent_rust_doc_comment_confusion=True)
        if func.get_retval().get_type().is_result_string():
            result += indent+'// The resulting string must be freed by calling cef_string_userfree_free().\n'
        parts = func.get_wrapped_rust_parts()
        result += wrap_code(indent+'pub fn '+parts['name']+'(&self'+
                            ''.join([', ' + arg for arg in parts['args']])+') -> '+
                            parts['retval']+' {')
        result += indent+'  if self.c_object.is_null() {\n'
        result += indent+'    panic!("called a CEF method on a null object")\n'
        result += indent+'  }\n'
        result += indent+'  unsafe {\n'
        result += indent+'    CefWrap::to_rust(\n'
        result += indent+'      ((*self.c_object).'+parts['name']+'.unwrap())(\n'
        result += indent+'        self.c_object'
        for argument in func.arguments:
            if argument.type.get_raw_rust()['format'] == 'single':
                result += ',\n' + indent + '        CefWrap::to_c(' + \
                        get_rust_identifier(argument.get_name()) + ')'
            else:
                result += ',\n' + indent + '        CefWrap::to_c(' + \
                        get_rust_identifier(argument.get_name() + '_count') + ')'
                result += ',\n' + indent + '        CefWrap::to_c(' + \
                        get_rust_identifier(argument.get_name()) + ')'
        result += '))\n'
        result += indent+'  }\n'
        result += indent+'}\n'
        if first:
            first = False
    return result

def make_wrapped_rust_static_funcs(funcs, filename, defined_names, translate_map, indent):
    result = ''
    first = True
    for func in funcs:
        comment = func.get_comment()
        if first or len(comment) > 0:
            result += '\n'+format_comment(comment,
                                          indent,
                                          translate_map,
                                          prevent_rust_doc_comment_confusion=True)
        if func.get_retval().get_type().is_result_string():
            result += indent+'// The resulting string must be freed by calling cef_string_userfree_free().\n'
        parts = func.get_wrapped_rust_parts()
        rust_class_name = get_raw_rust_name(func.parent.name, False)
        rust_module_name = get_rust_user_module_name(filename)
        result += wrap_code(indent+'pub fn '+parts['name']+'('+
                            ', '.join(parts['args'])+') -> '+
                            parts['retval']+' {')
        result += indent+'  unsafe {\n'
        result += indent+'    CefWrap::to_rust(\n'
        result += indent+'      ::'+rust_module_name+'::'+rust_class_name+'_'+parts['name']+'(\n'
        first_arg = True
        for argument in func.arguments:
            if first_arg:
                first_arg = False
            else:
                result += ',\n'
            if argument.type.get_raw_rust()['format'] == 'single':
                result += indent + '        CefWrap::to_c(' + \
                        get_rust_identifier(argument.get_name()) + ')'
            else:
                result += indent + '        CefWrap::to_c(' + \
                        get_rust_identifier(argument.get_name() + '_count') + ')'
                result += indent + '        CefWrap::to_c(' + \
                        get_rust_identifier(argument.get_name()) + ')'
        result += '))\n'
        result += indent+'  }\n'
        result += indent+'}\n'
        if first:
            first = False
    return result

def make_rust_bindings(header, filename):
    # structure names that have already been defined
    defined_names = header.get_defined_structs()
    
    # map of strings that will be changed in C++ comments
    translate_map = header.get_capi_translations()
    
    # header string
    result = \
"""// Copyright (c) $YEAR$ Marshall A. Greenblatt. All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are
// met:
//
//    * Redistributions of source code must retain the above copyright
// notice, this list of conditions and the following disclaimer.
//    * Redistributions in binary form must reproduce the above
// copyright notice, this list of conditions and the following disclaimer
// in the documentation and/or other materials provided with the
// distribution.
//    * Neither the name of Google Inc. nor the name Chromium Embedded
// Framework nor the names of its contributors may be used to endorse
// or promote products derived from this software without specific prior
// written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
// "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
// LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
// A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
// OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
// SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
// LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
// DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
// THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
// (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
// OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
//
// ---------------------------------------------------------------------------
//
// This file was generated by the CEF translator tool and should not be edited
// by hand. See the translator.README.txt file in the tools directory for
// more information.
//

#![allow(non_snake_case, unused_imports)]

use eutil;
use interfaces;
use types;
use wrappers::CefWrap;

use libc;
use std::collections::HashMap;
use std::ptr;
"""
    classes = header.get_classes(filename)

    # output classes
    for cls in classes:
        # write raw Rust API
        # virtual functions are inside the structure
        raw_classname = cls.get_capi_name()
        result += '\n'+format_comment(cls.get_comment(),
                                      '',
                                      translate_map,
                                      prevent_rust_doc_comment_confusion=True);
        result += '#[repr(C)]\n'
        result += 'pub struct _'+raw_classname+ \
                ' {\n  //\n  // Base structure.\n  //\n  pub base: types::cef_base_t,\n'
        funcs = cls.get_virtual_funcs()
        result += make_raw_rust_member_funcs(funcs, defined_names, translate_map, '  ')
        result += '\n'
        result += '  //\n'
        result += '  // The reference count. This will only be present for Rust instances!\n'
        result += '  //\n'
        result += '  pub ref_count: uint,\n\n'
        result += '  //\n'
        result += '  // Extra data. This will only be present for Rust instances!\n'
        result += '  //\n'
        result += '  pub extra: u8,\n'
        result += '} \n\npub type '+raw_classname+' = _'+raw_classname+';\n\n'

        # write wrapped Rust API
        wrapped_classname = cls.get_wrapped_rust_name(False)
        static_funcs = cls.get_static_funcs()
        result += '\n'+format_comment(cls.get_comment(),
                                      '',
                                      translate_map,
                                      prevent_rust_doc_comment_confusion=True);
        result += 'pub struct '+wrapped_classname+ ' {\n'
        result += '  c_object: *mut ' + raw_classname + ',\n'
        result += '}\n\n'
        result += 'impl Clone for '+wrapped_classname+' {\n'
        result += '  fn clone(&self) -> '+wrapped_classname+'{\n'
        result += '    unsafe {\n'
        result += '      if !self.c_object.is_null() {\n'
        result += '        ((*self.c_object).base.add_ref.unwrap())(&mut (*self.c_object).base);\n'
        result += '      }\n'
        result += '      '+wrapped_classname+' {\n'
        result += '        c_object: self.c_object,\n'
        result += '      }\n'
        result += '    }\n'
        result += '  }\n'
        result += '}\n\n'
        result += 'impl Drop for '+wrapped_classname+' {\n'
        result += '  fn drop(&mut self) {\n'
        result += '    unsafe {\n'
        result += '      if !self.c_object.is_null() {\n'
        result += '        ((*self.c_object).base.release.unwrap())(&mut (*self.c_object).base);\n'
        result += '      }\n'
        result += '    }\n'
        result += '  }\n'
        result += '}\n\n'
        result += 'impl '+wrapped_classname+' {\n'
        result += '  pub unsafe fn from_c_object(c_object: *mut '+raw_classname+') -> '+ \
            wrapped_classname+' {\n'
        result += '    '+wrapped_classname+' {\n'
        result += '      c_object: c_object,\n'
        result += '    }\n'
        result += '  }\n\n'
        result += '  pub unsafe fn from_c_object_addref(c_object: *mut '+raw_classname+') -> '+ \
            wrapped_classname+' {\n'
        result += '    if !c_object.is_null() {\n'
        result += '      ((*c_object).base.add_ref.unwrap())(&mut (*c_object).base);\n'
        result += '    }\n'
        result += '    '+wrapped_classname+' {\n'
        result += '      c_object: c_object,\n'
        result += '    }\n'
        result += '  }\n\n'
        result += '  pub fn c_object(&self) -> *mut '+raw_classname+' {\n'
        result += '    self.c_object\n'
        result += '  }\n\n'
        result += '  pub fn c_object_addrefed(&self) -> *mut '+raw_classname+' {\n'
        result += '    unsafe {\n'
        result += '      if !self.c_object.is_null() {\n'
        result += '        eutil::add_ref(self.c_object as *mut types::cef_base_t);\n'
        result += '      }\n'
        result += '      self.c_object\n'
        result += '    }\n'
        result += '  }\n\n'
        result += '  pub fn is_null_cef_object(&self) -> bool {\n'
        result += '    self.c_object.is_null()\n'
        result += '  }\n'
        result += '  pub fn is_not_null_cef_object(&self) -> bool {\n'
        result += '    !self.c_object.is_null()\n'
        result += '  }\n'
        result += make_wrapped_rust_member_funcs(funcs, defined_names, translate_map, '  ')
        result += make_wrapped_rust_static_funcs(static_funcs,
                                                 filename,
                                                 defined_names,
                                                 translate_map,
                                                 '  ')
        result += '} \n\n'
        result += 'impl CefWrap<*mut '+raw_classname+'> for '+wrapped_classname+' {\n'
        result += '  fn to_c(rust_object: '+wrapped_classname+') -> *mut '+raw_classname+' {\n'
        result += '    rust_object.c_object_addrefed()\n'
        result += '  }\n'
        result += '  unsafe fn to_rust(c_object: *mut '+raw_classname+') -> '+wrapped_classname+ \
                ' {\n'
        result += '    '+wrapped_classname+'::from_c_object_addref(c_object)\n'
        result += '  }\n'
        result += '}\n'
        result += 'impl CefWrap<*mut '+raw_classname+'> for Option<'+wrapped_classname+'> {\n'
        result += '  fn to_c(rust_object: Option<'+wrapped_classname+'>) -> *mut '+raw_classname+ \
                ' {\n'
        result += '    match rust_object {\n'
        result += '      None => ptr::null_mut(),\n'
        result += '      Some(rust_object) => rust_object.c_object_addrefed(),\n'
        result += '    }\n'
        result += '  }\n'
        result += '  unsafe fn to_rust(c_object: *mut '+raw_classname+') -> ' +\
                'Option<'+wrapped_classname+'> {\n'
        result += '    if c_object.is_null() {\n'
        result += '      None\n'
        result += '    } else {\n'
        result += '      Some(' + wrapped_classname + '::from_c_object_addref(c_object))\n'
        result += '    }\n'
        result += '  }\n'
        result += '}\n\n'

        defined_names.append(cls.get_capi_name())
        
        # TODO(pcwalton): Do something with global functions?

    # add the copyright year
    result = result.replace('$YEAR$', get_year())
    
    return result


def write_rust_bindings(header, filepath, backup):
    rust_path = get_rust_file_name(filepath)
    if path_exists(rust_path):
        oldcontents = read_file(rust_path)
    else:
        oldcontents = ''

    filename = os.path.split(filepath)[1]
    newcontents = make_rust_bindings(header, filename)
    if newcontents != oldcontents:
        if backup and oldcontents != '':
            backup_file(rust_path)
        write_file(rust_path, newcontents)
        return True
    
    return False

