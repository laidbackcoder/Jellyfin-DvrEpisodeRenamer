# Jellyfin-DvrEpisodeRenamer

This application can be used to automatically rename a Jellyfin recorded TV
file using the metadata stored in a .nfo file which is saved alongside the
video file by Jellyfin's DVR functionality.


There are two modes of processing:

* Single Video file
* Whole directory (including sub-directories)

This is determined by the path supplied to the application when executed.

By default the application looks for .ts files, however .mp4 & .m4v files can be
specified.


The associated meta data files (episode info and thumbnail) will also be renamed
unless the delete option has been used, in which case they will be deleted.


## Manual Usage

```
usage: Jellyfin-DvrEpisodeRenamer.py [-h] [-d | -r] [-e {.ts,.mp4,.m4v}] path

Auto Rename Jellyfin TV Show Recordings (DVR)

positional arguments:
  path                  Path to File or Directory to Process

options:
  -h, --help            show this help message and exit
  -d, --delete          Delete the episiode info file and thumbnail after processing
  -r, --rename          Rename the episiode info file and thumbnail after processing (default)
  -e {.ts,.mp4,.m4v}, --extension {.ts,.mp4,.m4v}
                        Video File Extension (default: .ts)
```

## Automation

### Jellyfin
[Jellyfin](https://github.com/jellyfin/jellyfin "JellyFin on GitHub") can be configured to call the application once a recording has finished:

_Dashboard > Live TV > Digital Recorder > Recording Post Processing_



### Docker-Post-Recording

I am a big fan of the [docker-post-recording](https://github.com/chacawaca/docker-post-recording "docker-post-recording on GitHub") project and us it to automatically remove commercials and transcode my recordings to a .mp4 file. It is possible to configure the tool to execute the Jellyfin-DvrEpisodeRenamer script automatically once the transcoding has been finished:

Copy the Jellyfin-DvrEpisodeRenamer.py file to the hooks directory in the docker container's config folder:

```Bash
/config/hooks/
```

Whilst in the hooks folder, create a file called 'post_conversion.sh', and populate with the following:

```Bash
#!/bin/sh
#
# Rename the file and handle the Meta Data post conversion
#
# The first parameter is the conversion status.  A value of 0 indicates that
# the video has been converted successfully.  Else, conversion failed.
#
# The second parameter is the full path to the converted video (the output).
#

CONVERSION_STATUS=$1
CONVERTED_FILE="$2"

if [ "$CONVERSION_STATUS" -eq 0 ]; then
    python3 /config/hooks/Jellyfin-DvrEpisodeRenamer.py "$CONVERTED_FILE" -e .mp4 -d
fi
```
This script will be executed once transcoding has been completed.
