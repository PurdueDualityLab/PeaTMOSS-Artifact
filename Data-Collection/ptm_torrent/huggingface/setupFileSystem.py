import ptm_torrent.huggingface as hf
from ptm_torrent.utils.fileSystem import checkFileSystem, setupFileSystem


def main() -> None:
    if checkFileSystem(rootFolderPath=hf.rootFolderPath, subfolderPaths=hf.subFolders):
        print("Filesystem has the correct structure")
        return None
    else:
        print("Creating Filesystem with correct structure")
        setupFileSystem(rootFolderPath=hf.rootFolderPath, subfolderPaths=hf.subFolders)


if __name__ == "__main__":
    main()
