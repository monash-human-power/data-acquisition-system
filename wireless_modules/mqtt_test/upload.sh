#!/bin/bash
rshell $@ "cp -r src/* /pyboard; rm /pyboard/config.example.py"