package easy.soc.hacks.frontend.controllers.rest

import easy.soc.hacks.frontend.domain.VideoFragment
import easy.soc.hacks.frontend.service.VideoFragmentService
import easy.soc.hacks.frontend.service.VideoService
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

    @PostMapping("video/{videoId}/fragment/{fragmentId}")
    fun pushFragment(
        @PathVariable("videoId") videoId: Long,
        @PathVariable("fragmentId") fragmentId: Long,
        @RequestHeader("X-Fragment-duration") fragmentDuration: Double,
        @RequestBody data: ByteArray
    ): ResponseEntity<Unit> {
        return try {
            val videoFragment = VideoFragment().apply {
                this.id = fragmentId
                this.duration = fragmentDuration
                this.data = data
                this.video = videoService.getVideoById(videoId).get()
            }
            videoFragmentService.save(videoFragment)

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
}