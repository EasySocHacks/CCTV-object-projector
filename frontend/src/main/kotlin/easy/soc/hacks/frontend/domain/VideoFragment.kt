package easy.soc.hacks.frontend.domain

class VideoFragment(
    val id: Long,
    val duration: Double,
    val data: ByteArray
)

open class VideoFragmentNode(
    val videoFragment: VideoFragment,
    var next: VideoFragmentNode? = null
)

class DummyVideoFragmentNode : VideoFragmentNode(VideoFragment(-1, 0.0, ByteArray(0)))