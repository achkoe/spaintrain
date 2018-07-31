USAGE="USage: crypt.sh d|e password"
if [[ "$1" != "d" ]] && [[ $1 != "e" ]] ; then
    echo $USAGE
    exit 1
fi
if [[ "$2" == "" ]] ; then
    echo $USAGE
    exit 1
fi
if [[ "$1" == "d" ]] ; then
    echo "decrpyting"
    openssl aes-128-cbc  -d -k $2 -in rawcontents.tar.gz.aes -out rawcontents.tar.gz
    tar -zxvf rawcontents.tar.gz
else
    echo "encrypting"
    tar -zvcf rawcontents.tar.gz process/rawcontents/*
    openssl aes-128-cbc  -salt -k $2 -in rawcontents.tar.gz -out rawcontents.tar.gz.aes
fi
