package easy.soc.hacks.frontend.controllers.rest

import easy.soc.hacks.frontend.domain.CameraVideo
import easy.soc.hacks.frontend.domain.ManifestNode
import easy.soc.hacks.frontend.domain.VideoFragment
import easy.soc.hacks.frontend.service.VideoFragmentStreamService
import org.springframework.http.HttpStatus.NOT_FOUND
import org.springframework.http.HttpStatus.NOT_MODIFIED
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*
import javax.servlet.http.HttpSession

@RestController
@RequestMapping("api/v1")
class StreamingController {
    companion object {
        // TODO: create storage. DB?
        val videoFragmentStreamServices = mutableMapOf(
            0L to VideoFragmentStreamService(
                CameraVideo(
                    0L,
                    "yt0",
                    "url0"
                )
            ),
            1L to VideoFragmentStreamService(
                CameraVideo(
                    1L,
                    "yt1",
                    "url1"
                )
            ),
            2L to VideoFragmentStreamService(
                CameraVideo(
                    2L,
                    "yt2",
                    "url2"
                )
            )
        )
        private const val httpSessionManifestNodeAttributeNameFormat = "VIDEO_%d_MANIFEST_NODE"
    }

    @PostMapping("video/{videoId}/fragment/{fragmentId}")
    fun pushFragment(
        @PathVariable("videoId") videoId: Long,
        @PathVariable("fragmentId") fragmentId: Long,
        @RequestHeader("X-Fragment-duration") fragmentDuration: Double,
        @RequestBody data: ByteArray
    ): ResponseEntity<Unit> {
        val videoFragment = VideoFragment(fragmentId, fragmentDuration, data)
        videoFragmentStreamServices[videoId]?.pushVideoFragment(videoFragment)
            ?: return ResponseEntity.status(NOT_FOUND).build()

        return ResponseEntity.ok().build()
    }

    @GetMapping("video/{videoId}/manifest")
    fun getManifest(
        @PathVariable("videoId") videoId: Long,
        httpSession: HttpSession
    ): ResponseEntity<ByteArray> {
        val httpSessionManifestNodeAttributeName = httpSessionManifestNodeAttributeNameFormat.format(videoId)

        if (httpSession.getAttribute(httpSessionManifestNodeAttributeName) == null) {
            val manifestNodeTail = videoFragmentStreamServices[videoId]?.tailManifestNode()
                ?: return ResponseEntity.status(NOT_FOUND).build()

            httpSession.setAttribute(httpSessionManifestNodeAttributeName, manifestNodeTail)
        }

        val previousManifestMode = httpSession.getAttribute(httpSessionManifestNodeAttributeName) as ManifestNode
        val manifestNode = previousManifestMode.next ?: return ResponseEntity.status(NOT_MODIFIED).build()

        httpSession.setAttribute(httpSessionManifestNodeAttributeName, manifestNode)

        return ResponseEntity.ok().body(manifestNode.manifest.data)
    }

    @GetMapping("video/{videoId}/fragment/{fragmentId}")
    fun getFragment(
        @PathVariable("videoId") videoId: Long,
        @PathVariable("fragmentId") fragmentId: Long,
        httpSession: HttpSession
    ): ResponseEntity<ByteArray> {
        val httpSessionManifestNodeAttributeName = httpSessionManifestNodeAttributeNameFormat.format(videoId)

        val manifestNode = httpSession.getAttribute(httpSessionManifestNodeAttributeName) as ManifestNode?
            ?: return ResponseEntity.status(NOT_FOUND).build()

        val videoFragmentNode = manifestNode.manifest.videoFragmentNodes.find {
            it.videoFragment.id == fragmentId
        } ?: return ResponseEntity.status(NOT_FOUND).build()

        return ResponseEntity.ok().body(videoFragmentNode.videoFragment.data)
    }
}