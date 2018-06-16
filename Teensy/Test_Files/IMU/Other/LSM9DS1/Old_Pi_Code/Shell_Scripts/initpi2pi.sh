#!/bin/sh

printf "\nGenerating ssh-keys....\n\n"
cat ~/.ssh/id_rsa.pub | ssh -o StrictHostKeyChecking=no pi@Primary.local "cat >> ~/.ssh/authorized_keys"
printf "\nSuccessfully generated ssh-keys\n\n"
