"""Current file format for the various text only notebook extensions"""

import os

FILE_FORMAT_VERSION = {
    # R markdown format
    '.Rmd': '1.0',
    # Version 1.0 on 2018-08-22 - nbrmd v0.5.2 : Initial version

    # Python scripts
    '.py': '1.0',
    # Version 1.0 on 2018-08-22 - nbrmd v0.5.2 : Initial version

    # Python scripts
    '.R': '1.0',
    # Version 1.0 on 2018-08-22 - nbrmd v0.5.2 : Initial version
}

FILE_FORMAT_VERSION_ORG = FILE_FORMAT_VERSION


def file_format_version(ext):
    """Return file format version for given ext"""
    return FILE_FORMAT_VERSION.get(ext)


def check_file_version(nb, source_path, outputs_path):
    """Raise if file version in source file would override outputs"""
    _, ext = os.path.splitext(source_path)
    current = file_format_version(ext)
    version = nb.metadata.get('nbrmd_format_version')
    if version:
        del nb.metadata['nbrmd_format_version']

    # Missing version, still generated by nbrmd?
    if nb.metadata and not version:
        version = current

    # Same version? OK
    if version == current:
        return

    # Not merging? OK
    if source_path == outputs_path:
        return

    raise ValueError("File {} has nbrmd_format_version={}, but "
                     "current version for that extension is {}.\n"
                     "It would not be safe to override the source of {} "
                     "with that file.\n"
                     "Please remove one or the other file."
                     .format(os.path.basename(source_path),
                             version, current,
                             os.path.basename(outputs_path)))
