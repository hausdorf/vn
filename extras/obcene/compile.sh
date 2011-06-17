#!/bin/bash
source classpath.sh
javac -Xlint:unchecked -classpath $CLASSPATH J2Reader.java
