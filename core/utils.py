import random
import string

# ===============================================================================
# Random string and Id generators
# ===============================================================================


# 16 digit random string for Ids
def randomstr():
    return "".join(
        random.choices(
            string.ascii_uppercase + string.ascii_lowercase + string.digits, k=16
        )
    )


def randomlongstr():
    return "".join(
        random.choices(
            string.ascii_uppercase + string.ascii_lowercase + string.digits, k=32
        )
    )


def randomlongslug():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=32))


# 64 digit random string for Public Links
def randomverylongstr():
    return "".join(
        random.choices(
            string.ascii_uppercase + string.ascii_lowercase + string.digits, k=64
        )
    )


def randomshortstr():
    return "".join(
        random.choices(
            string.ascii_uppercase + string.ascii_lowercase + string.digits, k=5
        )
    )


def randomnumberstr():
    return "".join(random.choices(string.digits, k=7))


def randomnumstr():
    return "".join(random.choices(string.digits, k=16))


def randomcode():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=5))


def randomverifycode():
    return "".join(random.choices(string.digits, k=5))


# 16 digit random string for Ids
def randomint():
    return "".join(random.choices(string.digits, k=16))


def randompassword():
    return "".join(
        random.choices(
            string.ascii_uppercase
            + string.ascii_lowercase
            + string.digits
            + string.punctuation,
            k=16,
        )
    )

def generate_model_id(length=32):
    characters = (
        string.ascii_letters + string.digits
    )  # Include letters (both cases) and digits
    return "".join(random.choice(characters) for _ in range(length))


def get_extension(mime_type):

    # --------------------------------------------------------------------------
    # Images
    # --------------------------------------------------------------------------

    # Jpeg image/jpeg
    if mime_type == "image/jpeg":
        return ".jpg"

    # Gif image/gif
    elif mime_type == "image/gif":
        return ".gif"

    # Png image/png
    elif mime_type == "image/png":
        return ".png"

    # Webp image/webp
    elif mime_type == "image/webp":
        return ".webp"

    # .bmp image/bmp
    elif mime_type == "image/bmp":
        return ".bmp"

    # .svg image/svg+xml
    elif mime_type == "image/svg+xml":
        return ".svg"

    # .tif image/tiff
    elif mime_type == "image/tiff":
        return ".tif"

    # .webp	image/webp
    elif mime_type == "image/webp":
        return ".webp"

    # --------------------------------------------------------------------------
    # Documents
    # --------------------------------------------------------------------------

    # Pdf application/pdf
    elif mime_type == "application/pdf":
        return ".pdf"

    # .csv text/csv
    elif mime_type == "text/csv":
        return ".csv"

    # .txt text/plain
    elif mime_type == "text/plain":
        return ".txt"

    # .doc application/msword
    elif mime_type == "application/msword":
        return ".doc"

    # .docx	application/vnd.openxmlformats-officedocument.wordprocessingml.document
    elif (
        mime_type
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        return ".docx"

    # .gz application/gzip
    elif mime_type == "application/gzip":
        return ".gz"

    # .ppt application/vnd.ms-powerpoint
    elif mime_type == "application/vnd.ms-powerpoint":
        return ".ppt"

    # .odp application/vnd.oasis.opendocument.presentation
    elif mime_type == "application/vnd.oasis.opendocument.presentation":
        return ".odp"

    # .ods application/vnd.oasis.opendocument.spreadsheet
    elif mime_type == "application/vnd.oasis.opendocument.spreadsheet":
        return ".ods"

    # .odt application/vnd.oasis.opendocument.text
    elif mime_type == "application/vnd.oasis.opendocument.text":
        return ".odt"

    # .pptx	application/vnd.openxmlformats-officedocument.presentationml.presentation
    elif (
        mime_type
        == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    ):
        return ".pptx"

    # .rar application/vnd.rar
    elif mime_type == "application/vnd.rar":
        return ".rar"

    # .rtf application/rtf
    elif mime_type == "application/rtf":
        return ".rtf"

    # .xls application/vnd.ms-excel
    elif mime_type == "application/vnd.ms-excel":
        return ".xls"

    # .xlsx	application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
    elif (
        mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ):
        return ".xlsx"

    # .zip application/zip
    elif mime_type == "application/zip":
        return ".zip"

    # .7z application/x-7z-compressed
    elif mime_type == "application/x-7z-compressed":
        return ".7z"

    # --------------------------------------------------------------------------
    # Audio
    # --------------------------------------------------------------------------

    # Mp3 audio/mpeg
    elif mime_type == "audio/mpeg":
        return ".mp3"

    # .m4a
    elif mime_type == "audio/mp4":
        return ".mp4"

    # .ogg audio/ogg
    elif mime_type == "audio/ogg":
        return ".ogg"

    # .mid audio/midi
    elif mime_type == "audio/midi":
        return ".mid"

    # .midi audio/x-midi
    elif mime_type == "audio/x-midi":
        return ".midi"

    # .opus audio/opus
    elif mime_type == "audio/opus":
        return ".opus"

    # .wav audio/wav
    elif mime_type == "audio/wav":
        return ".wav"

    # .weba	audio/webm
    elif mime_type == "audio/webm":
        return ".weba"

    # .3gp audio/3gpp
    elif mime_type == "audio/3gpp":
        return ".3gp"

    # .3g2 audio/3gpp2
    elif mime_type == "audio/3gpp2":
        return ".3g2"

    # --------------------------------------------------------------------------
    # Video
    # --------------------------------------------------------------------------

    # Mov video/quicktime
    elif mime_type == "video/quicktime":
        return ".mov"

    # Mp4 video/mp4
    elif mime_type == "video/mp4":
        return ".mp4"

    # .ogg audio/ogg
    elif mime_type == "video/ogg":
        return ".ogg"

    # .mpeg	video/mpeg
    elif mime_type == "video/mpeg":
        return ".mpeg"

    # 3gp video/3gpp
    elif mime_type == "video/3gpp":
        return ".3gp"

    # .3g2 video/3gpp2
    elif mime_type == "video/3gpp2":
        return ".3g2"

    # .ts video/mp2t
    elif mime_type == "video/mp2t":
        return ".ts"

    # .webm	video/webm
    elif mime_type == "video/webm":
        return ".webm"

    # --------------------------------------------------------------------------
    # Other
    # --------------------------------------------------------------------------

    # .apk application/vnd.android.package-archive
    elif mime_type == "application/vnd.android.package-archive":
        return ".apk"

    # .ogx application/ogg
    elif mime_type == "application/ogg":
        return ".ogx"

    # .swf application/x-shockwave-flash
    elif mime_type == "application/x-shockwave-flash":
        return ".swf"

    # .tar application/x-tar
    elif mime_type == "application/x-tar":
        return ".tar"

    else:
        return ""


def get_file_display_type(mime_type):

    # --------------------------------------------------------------------------
    # Images
    # --------------------------------------------------------------------------

    # Jpeg image/jpeg
    if mime_type == "image/jpeg":
        return "image"

    # Gif image/gif
    elif mime_type == "image/gif":
        return "image"

    # Png image/png
    elif mime_type == "image/png":
        return "image"

    # Webp image/webp
    elif mime_type == "image/webp":
        return "image"

    # .bmp image/bmp
    elif mime_type == "image/bmp":
        return "image"

    # .svg image/svg+xml
    elif mime_type == "image/svg+xml":
        return "image"

    # .tif image/tiff
    elif mime_type == "image/tiff":
        return "image"

    # .webp	image/webp
    elif mime_type == "image/webp":
        return "image"

    # --------------------------------------------------------------------------
    # Documents
    # --------------------------------------------------------------------------

    # Pdf application/pdf
    elif mime_type == "application/pdf":
        return "file"

    # .csv text/csv
    elif mime_type == "text/csv":
        return "file"

    # .txt text/plain
    elif mime_type == "text/plain":
        return "file"

    # .doc application/msword
    elif mime_type == "application/msword":
        return "file"

    # .docx	application/vnd.openxmlformats-officedocument.wordprocessingml.document
    elif (
        mime_type
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        return "file"

    # .gz application/gzip
    elif mime_type == "application/gzip":
        return "file"

    # .ppt application/vnd.ms-powerpoint
    elif mime_type == "application/vnd.ms-powerpoint":
        return "file"

    # .odp application/vnd.oasis.opendocument.presentation
    elif mime_type == "application/vnd.oasis.opendocument.presentation":
        return "file"

    # .ods application/vnd.oasis.opendocument.spreadsheet
    elif mime_type == "application/vnd.oasis.opendocument.spreadsheet":
        return "file"

    # .odt application/vnd.oasis.opendocument.text
    elif mime_type == "application/vnd.oasis.opendocument.text":
        return "file"

    # .pptx	application/vnd.openxmlformats-officedocument.presentationml.presentation
    elif (
        mime_type
        == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    ):
        return "file"

    # .rar application/vnd.rar
    elif mime_type == "application/vnd.rar":
        return "file"

    # .rtf application/rtf
    elif mime_type == "application/rtf":
        return "file"

    # .xls application/vnd.ms-excel
    elif mime_type == "application/vnd.ms-excel":
        return "file"

    # .xlsx	application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
    elif (
        mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ):
        return "file"

    # .zip application/zip
    elif mime_type == "application/zip":
        return "file"

    # .7z application/x-7z-compressed
    elif mime_type == "application/x-7z-compressed":
        return "file"

    # --------------------------------------------------------------------------
    # Audio
    # --------------------------------------------------------------------------

    # Mp3 audio/mpeg
    elif mime_type == "audio/mpeg":
        return "audio"

    # .m4a
    elif mime_type == "audio/mp4":
        return "audio"

    # .ogg audio/ogg
    elif mime_type == "audio/ogg":
        return "audio"

    # .mid audio/midi
    elif mime_type == "audio/midi":
        return "audio"

    # .midi audio/x-midi
    elif mime_type == "audio/x-midi":
        return "audio"

    # .opus audio/opus
    elif mime_type == "audio/opus":
        return "audio"

    # .wav audio/wav
    elif mime_type == "audio/wav":
        return "audio"

    # .weba	audio/webm
    elif mime_type == "audio/webm":
        return "audio"

    # .3gp audio/3gpp
    elif mime_type == "audio/3gpp":
        return "audio"

    # .3g2 audio/3gpp2
    elif mime_type == "audio/3gpp2":
        return "audio"

    # --------------------------------------------------------------------------
    # Video
    # --------------------------------------------------------------------------

    # Mov video/quicktime
    elif mime_type == "video/quicktime":
        return "video"

    # Mp4 video/mp4
    elif mime_type == "video/mp4":
        return "video"

    # .ogg audio/ogg
    elif mime_type == "video/ogg":
        return "video"

    # .mpeg	video/mpeg
    elif mime_type == "video/mpeg":
        return "video"

    # 3gp video/3gpp
    elif mime_type == "video/3gpp":
        return "video"

    # .3g2 video/3gpp2
    elif mime_type == "video/3gpp2":
        return "video"

    # .ts video/mp2t
    elif mime_type == "video/mp2t":
        return "video"

    # .webm	video/webm
    elif mime_type == "video/webm":
        return "video"

    # --------------------------------------------------------------------------
    # Other
    # --------------------------------------------------------------------------

    # .apk application/vnd.android.package-archive
    elif mime_type == "application/vnd.android.package-archive":
        return "file"

    # .ogx application/ogg
    elif mime_type == "application/ogg":
        return "file"

    # .swf application/x-shockwave-flash
    elif mime_type == "application/x-shockwave-flash":
        return "file"

    # .tar application/x-tar
    elif mime_type == "application/x-tar":
        return "file"

    else:
        return "Unknown"
