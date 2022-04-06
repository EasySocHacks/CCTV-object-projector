package easy.soc.hacks.frontend.controller.rest

import com.fasterxml.jackson.databind.JsonNode
import easy.soc.hacks.frontend.domain.*
import easy.soc.hacks.frontend.service.*
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.http.HttpStatus.INTERNAL_SERVER_ERROR
import org.springframework.http.HttpStatus.NOT_FOUND
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*
import java.util.*
import java.util.concurrent.ConcurrentSkipListSet
import java.util.concurrent.atomic.AtomicLong
import javax.servlet.http.HttpSession

@RestController
@RequestMapping("api/v1")
class StreamingController {
    @Autowired
    private lateinit var videoService: VideoService

    @Autowired
    private lateinit var videoFragmentService: VideoFragmentService

    @Autowired
    private lateinit var videoScreenshotService: VideoScreenshotService

    @Autowired
    private lateinit var projectionService: ProjectionService

    @Autowired
    private lateinit var sessionService: SessionService

    @Autowired
    private lateinit var messageService: MessageService

    private fun checkProcessedBatch(httpSession: HttpSession) {
        val session = sessionService.getStreamingSession().get()
        val nextBatchRef = httpSession.getAttribute("nextBatchId") as AtomicLong
        val currentBatchId = nextBatchRef.get()

        @Suppress("UNCHECKED_CAST")
        val processedVideoFragmentIdSet =
            httpSession.getAttribute("processedVideoFragmentIdSet")
                    as ConcurrentSkipListSet<VideoFragmentId>

        @Suppress("UNCHECKED_CAST")
        val processedMapBatchIdSet = httpSession.getAttribute("processedMapBatchIdSet")
                as ConcurrentSkipListSet<Long>

        val videoIds = videoService.findVideosBySessionId(session.id)
        val videoFragmentIds = videoIds.map {
            VideoFragmentId(
                id = currentBatchId,
                videoId = it.id,
                sessionId = session.id
            )
        }

        if (processedVideoFragmentIdSet.containsAll(videoFragmentIds) && processedMapBatchIdSet.contains(currentBatchId)) {
            if (
                nextBatchRef.compareAndSet(
                    currentBatchId,
                    currentBatchId + 1
                )
            ) {
                processedVideoFragmentIdSet.removeAll(videoFragmentIds.toSet())
                processedMapBatchIdSet.remove(currentBatchId)
            }
        }
    }

    @PostMapping("session/batch/{batchId}")
    fun postFragment(
        @PathVariable("batchId") batchId: Long,
        @RequestBody json: JsonNode
    ): ResponseEntity<Unit> {
        try {
            val session = sessionService.getStreamingSession().get()

            val fragmentsJson = json.get("fragments")
            val projectionsJson = json.get("projections")

            for (i in 0 until fragmentsJson.size()) {
                val fragmentJson = fragmentsJson.get(i)

                val duration = fragmentJson.get("duration").asDouble()
                val videoId = fragmentJson.get("videoId").asLong()

                val data = Base64.getDecoder().decode(fragmentJson.get("data").textValue())

                try {
                    videoFragmentService.save(
                        VideoFragment(
                            id = batchId,
                            video = videoService.findVideoById(
                                id = videoId
                            ).get(),
                            duration = duration,
                            data = data
                        )
                    )
                } catch (e: NoSuchElementException) {
                    return ResponseEntity.status(NOT_FOUND).build()
                }
            }

            for (i in 0 until projectionsJson.size()) {
                val projectionJson = projectionsJson.get(i)

                val frameId = projectionJson.get("frameId").asLong()

                val pointsJson = projectionJson.get("points")

                for (j in 0 until pointsJson.size()) {
                    val pointJson = pointsJson.get(j)

                    projectionService.save(
                        Projection(
                            frameId = frameId,
                            batchId = batchId,
                            session = session,
                            x = pointJson.get("x").asDouble(),
                            y = pointJson.get("y").asDouble(),
                            radius = pointJson.get("radius").asDouble()
                        )
                    )
                }
            }
        } catch (e: Exception) {
            println(e)
            println(e.stackTrace)
            println()
            return ResponseEntity.status(INTERNAL_SERVER_ERROR).build()
        }

        return ResponseEntity.ok().build()
    }

    @GetMapping("session/projection")
    fun getProjection(
        httpSession: HttpSession
    ): ResponseEntity<List<Projection>> {
        try {
            while (true) {
                val session = sessionService.getStreamingSession().get()

                @Suppress("UNCHECKED_CAST")
                val processedMapBatchIdSet = httpSession.getAttribute("processedMapBatchIdSet")
                        as ConcurrentSkipListSet<Long>

                val nextBatchIdRef = httpSession.getAttribute("nextBatchId") as AtomicLong
                val currentBatchId = nextBatchIdRef.get()

                val projectionList = projectionService.findProjectionsByBatchIdAndSessionId(
                    currentBatchId,
                    session.id
                )

                processedMapBatchIdSet.add(currentBatchId)

                Thread {
                    checkProcessedBatch(httpSession)
                }.start()

                return ResponseEntity.ok().body(projectionList)
            }
        } catch (e: NoSuchElementException) {
            return ResponseEntity.status(NOT_FOUND).build()
        } catch (e: Exception) {
            return ResponseEntity.status(INTERNAL_SERVER_ERROR).build()
        }
    }

    @GetMapping("video/manifest")
    fun getManifest(
        @RequestParam("id") videoId: Long,
        httpSession: HttpSession
    ): ResponseEntity<ByteArray> {
        try {
            val session = sessionService.getStreamingSession().get()

            @Suppress("UNCHECKED_CAST")
            val processedVideoVideoFragmentIdSet =
                httpSession.getAttribute("processedVideoFragmentIdSet")
                        as ConcurrentSkipListSet<VideoFragmentId>

            val nextBatchIdRef = httpSession.getAttribute("nextBatchId") as AtomicLong
            val currentBatchId = nextBatchIdRef.get()

            val manifest = videoFragmentService.getManifestByVideoIdAndSessionIdAndNextBatchId(
                videoId = videoId,
                sessionId = session.id,
                nextBatchId = currentBatchId
            )

            processedVideoVideoFragmentIdSet.add(
                VideoFragmentId(
                    id = currentBatchId,
                    videoId = videoId,
                    sessionId = session.id
                )
            )

            Thread {
                checkProcessedBatch(httpSession)
            }.start()

            return ResponseEntity.ok().body(manifest)
        } catch (e: NoSuchElementException) {
            return ResponseEntity.status(NOT_FOUND).build()
        } catch (e: Exception) {
            println(e)
            println()
            return ResponseEntity.status(INTERNAL_SERVER_ERROR).build()
        }
    }

    @GetMapping("video/fragment")
    fun getFragment(
        @RequestParam("id") videoId: Long,
        @RequestParam("fragment") fragmentId: Long
    ): ResponseEntity<ByteArray> {
        return try {
            ResponseEntity.ok().body(
                videoFragmentService.findVideoFragment(
                    id = fragmentId,
                    video = videoService.findVideoById(
                        id = videoId
                    ).get()
                ).get().data
            )
        } catch (e: NoSuchElementException) {
            ResponseEntity.status(NOT_FOUND).build()
        } catch (e: Exception) {
            ResponseEntity.status(INTERNAL_SERVER_ERROR).build()
        }
    }

    @PostMapping("video/screenshot")
    fun postScreenshot(
        @RequestParam("id") videoId: Long,
        @RequestParam("session") sessionId: String,
        @RequestBody data: ByteArray
    ): ResponseEntity<Unit> {
        videoScreenshotService.save(
            VideoScreenshot(
                video = videoService.findVideoById(
                    id = videoId
                ).get(),
                data = data
            )
        )

        return ResponseEntity.ok().build()
    }

    @GetMapping("video/screenshot")
    fun getScreenshot(
        @RequestParam("id") videoId: Long,
        httpSession: HttpSession
    ): ResponseEntity<ByteArray> {
        val video = videoService.findVideoById(videoId).orElseGet { null }

        if (video == null) {
            messageService.sendMessage(
                httpSession,
                "message.video.not.found",
                MessageType.ERROR
            )

            return ResponseEntity.status(NOT_FOUND).build()
        }

        val screenshotOptional = videoScreenshotService.findVideoScreenshotByVideo(video)

        return if (screenshotOptional.isPresent) {
            ResponseEntity.ok().body(screenshotOptional.get().data)
        } else {
            ResponseEntity.status(NOT_FOUND).build()
        }
    }
}