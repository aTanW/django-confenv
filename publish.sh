#!/bin/bash
#

#if [ -z "$1" ]; then
#  echo "Usage: $0 [ <packname> ]"
#  exit 1
#fi

function shortdir() { (
  cd $1
  dn="$(pwd -P)"
  echo "${dn/*\/}"
) }

if [ -z "$1" ]; then
  if [ -n "$CI_PROJECT_NAME" ]; then
    _myName="$CI_PROJECT_NAME"
  else
    if [ -n "$CI_PROJECT_DIR" ]; then
      _myName="$(shortdir $CI_PROJECT_DIR)"
    else
      _myDir=${0%/*}
      test "$_myDir" = "$0" && _myDir='.'
      _myName="$(shortdir $_myDir)"
    fi
  fi
else
  _myName="$1"
fi
_myName=${_myName/.deb}
echo "%PUBLISH% My name is $_myName"

_tempf="$(mktemp)"

function signdata() {
  local _orig _lbl

  echo
  echo "%PUBLISH% Creating command data for singing"

  _orig="SFTDCC"
  test -n "$REPO_ORIGIN" && _orig="$REPO_ORIGIN"

  _lbl="SFTDCC"
  test -n "$REPO_LABEL" && _lbl="$REPO_LABEL"

  echo '{"Origin":"'$_orig'","Label":"'$_lbl'","Signing":{' >$_tempf
  if [ -n "$REPO_GPGKEY" ]; then
    echo -n '"GpgKey":"'$REPO_GPGKEY'"' >>$_tempf
  fi
  if [ -n "$REPO_GPGFILE" ]; then
    if [ "${REPO_GPGFILE:0:1}" = "/" ]; then
      _passpath="$REPO_GPGFILE"
    else
      _passpath="/home/aptly/.gnupg/$REPO_GPGFILE"
    fi
    echo -n ',"Batch":true,"PassphraseFile":"'$_passpath'"' >>$_tempf
  elif [ -n "$REPO_GPGPASS" ]; then
    echo -n ',"Batch":true,"Passphrase":"'$REPO_GPGPASS'"' >>$_tempf
  fi
  echo "}}" >> $_tempf

  echo "====="
  cat $_tempf
  echo "====="
}

set -e

echo "%PUBLISH% Repo at $REPO_MGRURL name $REPO_NAME distribution $REPO_DIST"
_ref="$(curl -s $REPO_MGRURL/api/repos/$REPO_NAME/packages?q=$_myName)"
echo "%PUBLISH% Got package ref: $_ref"

if [ "$_ref" != "[]" ]; then
  echo '{"PackageRefs": ' > $_tempf
  echo -n "$_ref" >> $_tempf
  echo -n "}" >> $_tempf

  echo "%PUBLISH% Removing old packages"
  curl -s -X DELETE -H 'Content-Type: application/json' --data @$_tempf\
	$REPO_MGRURL/api/repos/$REPO_NAME/packages

  signdata

  echo
  echo "%PUBLISH% Publishing repo for $REPO_DIST"
  curl -s -X PUT -H 'Content-Type: application/json' --data @$_tempf\
        $REPO_MGRURL/api/publish/:./$REPO_DIST
else
  signdata
fi

for _item in deb_dist/*.deb ; do
  echo
  echo "%PUBLISH% Uploading package $_item"
  curl -s -X POST -F file=@$_item $REPO_MGRURL/api/files/$_myName
done

echo
echo "%PUBLISH% Publishing package(-s)"
curl -s -X POST $REPO_MGRURL/api/repos/$REPO_NAME/file/$_myName

echo
echo "%PUBLISH% Publishing repo with package for $REPO_DIST"
curl -s -X PUT -H 'Content-Type: application/json' --data @$_tempf\
        $REPO_MGRURL/api/publish/:./$REPO_DIST


# EOF publish.sh
