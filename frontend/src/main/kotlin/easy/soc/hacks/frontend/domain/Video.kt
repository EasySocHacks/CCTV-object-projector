package easy.soc.hacks.frontend.domain

import lombok.Generated

abstract class Video(
    @Generated
    var id: Long?,
    val name: String,
)

class CameraVideo(
    id: Long?,
    name: String,
    val url: String
) : Video(id, name)

class FileVideo(
    id: Long?,
    name: String,
    val path: String
) : Video(id, name)