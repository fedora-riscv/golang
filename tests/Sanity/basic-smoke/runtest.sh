#!/bin/bash
# vim: dict+=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   runtest.sh of /tools/golang/Sanity/basic-smoke
#   Description: basic smoke test for go
#   Author: Edjunior Machado <emachado@redhat.com>
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Copyright (c) 2019 Red Hat, Inc.
#
#   This program is free software: you can redistribute it and/or
#   modify it under the terms of the GNU General Public License as
#   published by the Free Software Foundation, either version 2 of
#   the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be
#   useful, but WITHOUT ANY WARRANTY; without even the implied
#   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#   PURPOSE.  See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see http://www.gnu.org/licenses/.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Include Beaker environment
. /usr/share/beakerlib/beakerlib.sh || exit 1

PACKAGE="$(rpm -qf $(which go))"

# Conserve the non-zero return value through the pipe
set -o pipefail

rlJournalStart
    rlPhaseStartSetup
        rlAssertRpm $PACKAGE
        rlRun "TmpDir=\$(mktemp -d)" 0 "Creating tmp directory"
        rlRun "pushd $TmpDir"
    rlPhaseEnd

    rlPhaseStartTest
        cat << EOF > $TmpDir/hello.go
package main
import "fmt"
func main() {
    fmt.Println("hello world")
}
EOF
        rlAssertExists "$TmpDir/hello.go"

        rlRun "go run $TmpDir/hello.go |& tee $TmpDir/go-run-hello.out" 0 "Testing 'go run'"
        rlAssertNotDiffer <(echo 'hello world') go-run-hello.out

        rlRun "go build -o $TmpDir/hello $TmpDir/hello.go" 0 "Testing 'go build'"
        rlAssertExists "hello"

        rlRun "$TmpDir/hello |& tee $TmpDir/hello.out" 0 "Running binary"
        rlAssertNotDiffer <(echo 'hello world') hello.out
    rlPhaseEnd

    rlPhaseStartCleanup
        rlRun "popd"
        rlRun "rm -r $TmpDir" 0 "Removing tmp directory"
    rlPhaseEnd
rlJournalPrintText
rlJournalEnd
