if [ "x$AL_DIR_120" == "x" ]; then
    echo "No AL_DIR_120, setting AL_DIR manually to /usr/local/NaoQiAcademics-1.2.0-Linux"
    export AL_DIR=/usr/local/NaoQiAcademics-1.2.0-Linux
else
    export AL_DIR=$AL_DIR_120
fi

