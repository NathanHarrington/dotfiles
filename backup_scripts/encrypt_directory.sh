#!/bin/bash
#
# Create a gpg-encrypted tar ball of everything in the directory:
# ~/Documents/auto_backup
#
# WATCH OUT - anything you put in there will be added to the tar ball.
# Huge, data inhibiting mistakes can be yours by adding symlinks,
# mounts, # etc.
#
# This is designed as part of nharrington's backup strategy to run every
# hour on the local system. See other crontab entries for
# synchronization to external backup systems of just the gpg file.
#
TMP_DIRECTORY=/home/nharrington/Documents
SRC_DIRECTORY=/home/nharrington/Documents/auto_backup
DEST_DIRECTORY=/home/nharrington/Documents/working_encrypted

HOSTNAME=$(hostname)
TAR_SRC_FILENAME="${HOSTNAME}_encrypted.tar"
TAR_GPG_FILENAME="${HOSTNAME}_encrypted.tar.gpg"

#echo "Create the destination working directory"
mkdir -p $DEST_DIRECTORY

#echo "Create tar file, overwrite any existing"
tar -cf $TMP_DIRECTORY/$TAR_SRC_FILENAME \
    $SRC_DIRECTORY

#echo "Encrypt the source tar file, put in destination directory"
gpg --output $DEST_DIRECTORY/$TAR_GPG_FILENAME \
    --encrypt --yes -r Nathan \
    $TMP_DIRECTORY/$TAR_SRC_FILENAME

#echo "Remove the temporary tar file"
rm $TMP_DIRECTORY/$TAR_SRC_FILENAME 
