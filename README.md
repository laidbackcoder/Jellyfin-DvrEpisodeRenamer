# Jellyfin-DvrEpisodeRenamer
Auto Rename Jellyfin DVR TV Show Recordings

    usage: Jellyfin-DvrEpisodeRenamer.py [-h] [-d | -r] [-e {.ts,.mp4,.m4v}] path

    Auto Rename Jellyfin DVR TV Show Recordings

    positional arguments:
      path                  Path to File or Directory to Process

    options:
      -h, --help            show this help message and exit
      -d, --delete          Delete the episiode info file and thumbnail after processing
      -r, --rename          Rename the episiode info file and thumbnail after processing (default)
      -e {.ts,.mp4,.m4v}, --extension {.ts,.mp4,.m4v}
                            Video File Extension (default: .ts)
