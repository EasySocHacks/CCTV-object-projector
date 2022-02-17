package easy.soc.hacks.frontend.domain

class Manifest(
    val id: Long,
    val videoFragmentNodes: List<VideoFragmentNode>,
    val data: ByteArray
)

open class ManifestNode(
    val manifest: Manifest,
    var next: ManifestNode? = null
)

object DummyManifestNode : ManifestNode(Manifest(-1, emptyList(), ByteArray(0)))