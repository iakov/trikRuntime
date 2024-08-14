#!/usr/bin/tclsh

# Copyright 2013-2014 Vladimir Nazarenko and Cybertech Labs Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Line cannot be too long

set maxLength 120

foreach fileName [getSourceFileNames] {
    set lineNumber 0
    foreach line [getAllLines $fileName] {
        incr lineNumber
        set line [string map {"\t" "    "} $line]
        if {[regexp {^[ \t]*//.+} $line]} {
	    continue
	}
        if {[string length $line] > $maxLength} {
            report $fileName $lineNumber "line is longer than $maxLength characters"
        }
    }
}
