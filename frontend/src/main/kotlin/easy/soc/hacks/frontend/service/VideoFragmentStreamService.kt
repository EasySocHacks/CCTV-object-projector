package easy.soc.hacks.frontend.service

import easy.soc.hacks.frontend.domain.*
import java.util.concurrent.ConcurrentHashMap


class VideoFragmentStreamService(
    val video: Video
) {
    init {
        fun manifestText(sequenceId: Long, fragmentList: List<VideoFragment>): String {
            return "#EXTM3U\n" +
                    "#EXT-X-VERSION:3\n" +
                    "#EXT-X-MEDIA-SEQUENCE:$sequenceId\n" +
                    "#EXT-X-TARGETDURATION:5\n" +
                    fragmentList.joinToString(separator = "\n") {
                        "#EXTINF:${it.duration},\nfragment/${it.id}"
                    }
        }

        Thread {
            var lastProcessedFragmentId: Long = -1L
            val manifestVideoFragmentNodeDeque = ArrayDeque<VideoFragmentNode>()

            while (true) {
                if (videoFragmentConcurrentMap.containsKey(lastProcessedFragmentId + 1)) {
                    val videoFragment = videoFragmentConcurrentMap.remove(lastProcessedFragmentId + 1)!!
                    val videoFragmentNode = VideoFragmentNode(videoFragment)

                    videoFragmentNodeTail.next = videoFragmentNode
                    videoFragmentNodeTail = videoFragmentNode

                    manifestVideoFragmentNodeDeque.add(videoFragmentNode)
                    if (manifestVideoFragmentNodeDeque.size > 5) {
                        manifestVideoFragmentNodeDeque.removeFirst()

                        val manifest = Manifest(
                            lastProcessedFragmentId + 1,
                            manifestVideoFragmentNodeDeque.toList(),
                            manifestText(
                                lastProcessedFragmentId + 1,
                                manifestVideoFragmentNodeDeque.map(VideoFragmentNode::videoFragment)
                            ).toByteArray()
                        )
                        val manifestNode = ManifestNode(manifest)
                        manifestNodeTail.next = manifestNode
                        manifestNodeTail = manifestNode
                    }

                    lastProcessedFragmentId++
                }
            }
        }.start()
    }

    // TODO: Force kill old fragments/manifests
    private val videoFragmentConcurrentMap = ConcurrentHashMap<Long, VideoFragment>()
    private var videoFragmentNodeTail: VideoFragmentNode = DummyVideoFragmentNode
    private var manifestNodeTail: ManifestNode = DummyManifestNode

    fun pushVideoFragment(videoFragment: VideoFragment) {
        videoFragmentConcurrentMap[videoFragment.id] = videoFragment
    }

    fun tailVideoFragmentNode(): VideoFragmentNode = videoFragmentNodeTail

    fun tailManifestNode(): ManifestNode = manifestNodeTail
}