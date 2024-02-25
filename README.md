# Jellyfin-DvrEpisodeRenamer

This application can be used to automatically rename a Jellyfin recorded TV
file using the metadata stored in a .inf file which is saved alongside the 
video file by Jellyfin's DVR functionality.


There are two modes of processing:

* Single Video file
* Whole directoy (incluiding sub-directories)

This is determined by the path supplied to the application when executed.


The associated meta data files (episode info and thumbnail) will also be renamed
unless the delete option has been used, in which case they will be deleted.


## Manual Usage

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
