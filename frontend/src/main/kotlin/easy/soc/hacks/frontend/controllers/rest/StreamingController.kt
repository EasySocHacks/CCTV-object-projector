package easy.soc.hacks.frontend.controllers.rest

import easy.soc.hacks.frontend.domains.VideoFragment
import easy.soc.hacks.frontend.domains.VideoScreenshot
import easy.soc.hacks.frontend.services.VideoFragmentService
import easy.soc.hacks.frontend.services.VideoScreenshotService
import easy.soc.hacks.frontend.services.VideoService
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.http.HttpStatus.INTERNAL_SERVER_ERROR
import org.springframework.http.HttpStatus.NOT_FOUND
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("api/v1")
class StreamingController {
    @Autowired
    private lateinit var videoService: VideoService

    @Autowired
    private lateinit var videoFragmentService: VideoFragmentService

    @Autowired
    private lateinit var videoScreenshotService: VideoScreenshotService

    @PostMapping("video/{videoId}/fragment/{fragmentId}")
    fun pushFragment(
        @PathVariable("videoId") videoId: Long,
        @PathVariable("fragmentId") fragmentId: Long,
        @RequestHeader("X-Fragment-duration") fragmentDuration: Double,
        @RequestBody data: ByteArray
    ): ResponseEntity<Unit> {
        return try {
            videoFragmentService.save(
                VideoFragment(
                    id = fragmentId,
                    duration = fragmentDuration,
                    data = data,
                    video = videoService.getVideoById(videoId).get()
                )
            )

            ResponseEntity.ok().build()
        } catch (e: NoSuchElementException) {
            ResponseEntity.status(NOT_FOUND).build()
        } catch (e: Exception) {
            ResponseEntity.status(INTERNAL_SERVER_ERROR).build()
        }
    }

    @GetMapping("video/{videoId}/manifest")
    fun getManifest(
        @PathVariable("videoId") videoId: Long
    ): ResponseEntity<ByteArray> {
        return try {
            ResponseEntity.ok().body(
                videoFragmentService.getLatestManifest(videoService.getVideoById(videoId).get())
            )
        } catch (e: NoSuchElementException) {
            ResponseEntity.status(NOT_FOUND).build()
        } catch (e: Exception) {
            ResponseEntity.status(INTERNAL_SERVER_ERROR).build()
        }
    }

    @GetMapping("video/{videoId}/fragment/{fragmentId}")
    fun getFragment(
        @PathVariable("videoId") videoId: Long,
        @PathVariable("fragmentId") fragmentId: Long
    ): ResponseEntity<ByteArray> {
        return try {
            ResponseEntity.ok().body(
                videoFragmentService.getVideoFragment(videoService.getVideoById(videoId).get(), fragmentId).get().data
            )
        } catch (e: NoSuchElementException) {
            ResponseEntity.status(NOT_FOUND).build()
        } catch (e: Exception) {
            ResponseEntity.status(INTERNAL_SERVER_ERROR).build()
        }
    }

    @PostMapping("video/{videoId}/screenshot")
    fun postScreenshot(
        @PathVariable("videoId") videoId: Long,
        @RequestBody data: ByteArray
    ): ResponseEntity<Unit> {
        videoScreenshotService.save(
            VideoScreenshot(
                video = videoService.getVideoById(videoId).get(),
                data = data
            )
        )

        return ResponseEntity.ok().build()
    }

    @GetMapping("video/{videoId}/screenshot")
    fun getScreenshot(
        @PathVariable("videoId") videoId: Long
    ): ResponseEntity<ByteArray> {
        return ResponseEntity.ok().body(
            videoScreenshotService.getVideoScreenshotByVideoId(videoId).get().data
        )
    }
}