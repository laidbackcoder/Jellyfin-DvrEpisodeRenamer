"""Jellyfin DVR Episode Renamer

This application can be used to automatically rename a Jellyfin recorded TV
file using the metadata stored in a .inf file which is automatically saved
alongside the video file by Jellyfin's DVR functionality.

Version: 1.1.0
License: MIT License
URL: https://github.com/laidbackcoder/Jellyfin-DvrEpisodeRenamer

Help Message (-h):

    usage: Jellyfin-DvrEpisodeRenamer.py [-h] [-d | -r]
                                        [-e {.ts,.mp4,.m4v}] path

    Auto Rename Jellyfin TV Show Recordings (DVR)

    positional arguments:
    path                  Path to File or Directory to Process

    options:
    -h, --help            show this help message and exit
    -d, --delete          Delete the episiode info file and thumbnail
                            after processing
    -r, --rename          Rename the episiode info file and thumbnail after
                            processing (default)
    -e {.ts,.mp4,.m4v}, --extension {.ts,.mp4,.m4v}
                            Video File Extension (default: .ts)


Example 'substitutions.json' file:
[
    {
        "original": "Rick and Morty [adult swim]",
        "replacement": "Rick and Morty"
    }
]

"""

# TODO: Update Doc Strings
# TODO: Update Readme
# TODO: Refactor .format() to f strings for consistency
# TODO: Move Regex and Substitutions into config file
# TODO: Verify format of JSON file

import argparse
import json
import os
import re
import xml.etree.ElementTree as xmlET


errors = 0
success = 0


def __handle_args():
    """Handle Command Line Arguments

    Returns:
        string: file path,
        string: file extension,
        bool: delete info file and thumbnail
    """
    parser = argparse.ArgumentParser(
        description="Auto Rename Jellyfin TV Show Recordings (DVR)"
    )
    parser.add_argument(
        "path",
        type=str,
        help="Path to File or Directory to Process"
        )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-d",
        "--delete",
        action="store_true",
        help="Delete the episiode info file and thumbnail after processing",
    )
    group.add_argument(
        "-r",
        "--rename",
        action="store_true",
        help="""Rename the episiode info file and thumbnail after
        processing (default)""",
    )
    parser.add_argument(
        "-e",
        "--extension",
        type=str,
        choices=[".ts", ".mp4", ".m4v"],
        default=".ts",
        help="Video File Extension (default: .ts)",
    )
    args = parser.parse_args()

    # Handle input arguments
    return args.path, args.extension, args.delete


def load_substitutions(substitutions_json_file):
    """Load Substitution Show Names from JSON file

    Returns:
        dictionary: Substitution Show Names
    """
    try:
        if os.path.exists(substitutions_json_file):
            with open(substitutions_json_file, "r") as json_in:
                return json.load(json_in)
        else:
            return []

    except Exception as e:
        print(
            "Error with JSON file, substitutions disabled: {}".format(
                e.message
                )
            )
        return []


def process_file(
        video_file_path,
        extn_video_file,
        delete_info_and_thumbnail_files,
        substitution_show_names
        ):
    """Process a specified Video File

    Args:
        video_file_path (string): Video File Path

    Raises:
        Exception: Generic Exception with Message
    """
    try:
        video_file_name = os.path.basename(video_file_path)
        path = os.path.dirname(video_file_path)

        print("\nProcessing file:", video_file_name)

        # Check if the file is a video file
        if video_file_name.endswith(extn_video_file):

            # Get file name without extension
            recording_id = os.path.splitext(video_file_name)[0]

            # Generate file names and paths for all associated files
            show_info_file_path = "{}/{}".format(path, "tvshow.nfo")
            info_file_name = "{}{}".format(recording_id, ".nfo")
            info_file_path = "{}/{}".format(path, info_file_name)
            thumbnail_file_name = "{}{}".format(recording_id, "-thumb.jpg")
            thumbnail_file_path = "{}/{}".format(path, thumbnail_file_name)

            # Check for an info file for the episode
            if os.path.exists(info_file_path):

                # Check for an info file for the show
                if os.path.exists(show_info_file_path):

                    # Extract the show name from the show info file
                    show_name = (
                        xmlET.parse(
                            show_info_file_path
                            ).getroot().find("title").text
                    )

                    print("Show Name extracted:", show_name)

                    # Apply any substitutions to the show name
                    for sub in substitution_show_names:
                        if show_name == sub["original"]:
                            show_name = sub["replacement"]
                            print("Show Name substituted:", show_name)

                    # Extract the plot text from the episode info file
                    plot = xmlET.parse(
                        info_file_path
                        ).getroot().find("plot").text

                    # Use regular expression to extract season and episode
                    # number from the plot text (adding leading zeroes if
                    # needed)
                    match = re.search(r"S(\d+)\s*Ep(\d+)", plot)
                    if match:
                        season = match.group(1).zfill(2)
                        episode = match.group(2).zfill(2)
                        episode_info = f"S{season}E{episode}"
                        print(
                            "Season and Episode info extracted:", episode_info
                            )

                        # Generate new name for the episode
                        new_recording_id = "{} - {}".format(
                            show_name,
                            episode_info
                            )
                        if new_recording_id != recording_id:
                            new_video_file_name = "{}{}".format(
                                new_recording_id, extn_video_file
                            )
                            new_video_file_path = "{}/{}".format(
                                path, new_video_file_name
                            )

                            # Handle Duplicates
                            copies = 1
                            while os.path.exists(new_video_file_path):
                                copies += 1
                                new_video_file_name = "{}({}){}".format(
                                    new_recording_id, copies, extn_video_file
                                )
                                new_video_file_path = "{}/{}".format(
                                    path, new_video_file_name
                                )
                            if copies > 1:
                                new_recording_id = "{}({})".format(
                                    new_recording_id, copies
                                )

                            # Rename the video file
                            try:
                                print(
                                    "Renaming Video File: from "
                                    "'{}' to '{}'.".format(
                                        video_file_name,
                                        new_video_file_name
                                    )
                                )
                                os.rename(video_file_path, new_video_file_path)
                            except Exception as e:
                                raise Exception(
                                    "Unable to rename file: {}".format(e)
                                    )

                            # Check if the episiode info file and thumbnail
                            # should be deleted or renamed
                            if delete_info_and_thumbnail_files:
                                # Delete the episode info file and thumbnail
                                try:
                                    print(
                                        "Deleting Info File:", info_file_name
                                        )
                                    os.remove(info_file_path)

                                    if os.path.exists(thumbnail_file_path):
                                        print(
                                            "Deleting Thumbnail File: " +
                                            thumbnail_file_name
                                        )
                                        os.remove(thumbnail_file_path)
                                except Exception as e:
                                    raise Exception(
                                        "Unable to delete file: {}".format(e)
                                    )
                            else:
                                # Rename the episiode info file and thumbnail
                                try:
                                    new_info_file_name = "{}.nfo".format(
                                        new_recording_id
                                    )
                                    new_info_file_path = "{}/{}".format(
                                        path, new_info_file_name
                                    )
                                    print(
                                        "Renaming Info File: from "
                                        "{} to {}".format(
                                            info_file_name,
                                            new_info_file_name
                                        )
                                    )
                                    os.rename(
                                        info_file_path,
                                        new_info_file_path
                                        )

                                    if os.path.exists(thumbnail_file_path):
                                        new_thumbnail_file_name = (
                                            f"{new_recording_id}-thumb.jpg"
                                        )
                                        new_thumbnail_file_path = (
                                            f"{path}/{new_thumbnail_file_name}"
                                        )
                                        print(
                                            "Renaming Thumbnail File: "
                                            "from {} to {}".format(
                                                thumbnail_file_name,
                                                new_thumbnail_file_name,
                                            )
                                        )
                                        os.rename(
                                            thumbnail_file_path,
                                            new_thumbnail_file_path
                                        )
                                except Exception as e:
                                    raise Exception(
                                        "Unable to rename file: {}".format(e)
                                    )
                            print("Done.")
                        else:
                            raise Exception("Episode already processed")
                    else:
                        raise Exception(
                            "Season and Episode info not "
                            "found in episode info file"
                        )
                else:
                    raise Exception("No tvshow.nfo show info file found")
            else:
                raise Exception("No matching .nfo file found for the episode")
        else:
            raise Exception(
                "Invalid file format: Must be a {} file".format(
                    extn_video_file
                    )
            )
    except Exception as e:
        raise Exception(e)


def process_directory(
        root_directory,
        extn_video_file,
        delete_info_and_thumbnail_files,
        substitution_show_names
        ):
    """Process Video Files and Sub Directories in a specified directory

    Args:
        root_directory (string): Directory Path

    Raises:
        Exception: Generic Exception with Message
    """

    global success
    global errors

    print("\nProcessing directory:", root_directory)

    try:
        # Loop through all files and sub directoties in the directory
        for item in os.listdir(root_directory):
            item_path = "{}/{}".format(root_directory, item)

            # Check if the item being processed is a sub directory
            if os.path.isdir(item_path):
                # Process the sub directory
                process_directory(item_path)
            else:
                # Process the file if it has the correct video file extension
                try:
                    if item.endswith(extn_video_file):
                        process_file(
                            item_path,
                            extn_video_file,
                            delete_info_and_thumbnail_files,
                            substitution_show_names
                            )
                        success += 1
                except Exception as e:
                    print(e, "\nSkipping file...")
                    errors += 1
    except Exception as e:
        raise Exception(e)


def run():
    global success
    global errors

    # Load the Command Line Arguments
    path, extn_video_file, delete_info_and_thumbnail_files = __handle_args()

    substitutions_json_file = os.path.dirname(
        os.path.realpath(__file__)
        ) + "/substitutions.json"

    # Load Substitution Show Names from JSON file
    substitution_show_names = load_substitutions(substitutions_json_file)

    # Check valid path has been supplied
    if os.path.exists(path):
        # Check if the path is to a directory or a file
        if os.path.isdir(path):
            # Process the directory
            try:
                process_directory(
                    path,
                    extn_video_file,
                    delete_info_and_thumbnail_files,
                    substitution_show_names
                    )
            except Exception as e:
                print("Error:", e)
        else:
            # Process the file if it has the correct video file extension
            try:
                if path.endswith(extn_video_file):
                    process_file(
                        path,
                        extn_video_file,
                        delete_info_and_thumbnail_files,
                        substitution_show_names
                        )
                    success += 1
            except Exception as e:
                print(e, "\nSkipping file...")
                errors += 1

        print(
            "\n--------------------------------------"
            "-----------------------------------------"
        )
        print(
            "Finished: Successfully processed "
            "{} file(s), Failed to process {} file(s)".format(
                success, errors
            )
        )
        print(
            "-----------------------------------------"
            "--------------------------------------\n"
        )
    else:
        print("\nError: Could not locate file or directory:", path)


if __name__ == "__main__":
    run()
