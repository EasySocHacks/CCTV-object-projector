package easy.soc.hacks.frontend.controllers.view

import easy.soc.hacks.frontend.component.BackendWebSocketHandlerComponent.Companion.activeBackendWebSocketSession
import easy.soc.hacks.frontend.domain.CalibrationPointListWrapper
import easy.soc.hacks.frontend.domain.CameraVideo
import easy.soc.hacks.frontend.domain.Video
import easy.soc.hacks.frontend.service.BackendBrokerService
import easy.soc.hacks.frontend.service.SequenceService
import easy.soc.hacks.frontend.service.VideoService
import easy.soc.hacks.frontend.service.VideoService.Companion.videoStatus
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Controller
import org.springframework.ui.Model
import org.springframework.ui.set
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.ModelAttribute
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.PostMapping

@Controller
class VideoController {
    @Autowired
    private lateinit var backendBrokerService: BackendBrokerService

    @Autowired
    private lateinit var sequenceService: SequenceService

    @Autowired
    private lateinit var videoService: VideoService

    @GetMapping("", "video/list/preview")
    fun previewVideoList(model: Model): String {
        model.addAttribute("videoList", videoService.findAll())
        model.addAttribute("videoStatus", videoStatus)

        return "index"
    }

    @GetMapping("video/add")
    fun addVideoGet(): String {
        return "addVideo"
    }

    @PostMapping("video/add")
    fun addVideoPost(@ModelAttribute cameraVideo: CameraVideo): String {
        val savedVideo = videoService.save(cameraVideo.apply {
            id = sequenceService.nextIdFor(Video.sequenceName)
        }) as CameraVideo
        backendBrokerService.appendCameraVideo(activeBackendWebSocketSession!!, savedVideo)

        return "redirect:/"
    }

    @GetMapping("video/{videoId}/calibration")
    fun calibrationVideo(@PathVariable("videoId") videoId: Long, model: Model): String {
        val video = videoService.getVideoById(videoId).get()

        model["video"] = video

        return "calibrationVideo"
    }

    @PostMapping("video/{videoId}/calibration/save")
    fun saveCalibration(
        @PathVariable("videoId") videoId: Long,
        @ModelAttribute calibrationPointListWrapper: CalibrationPointListWrapper
    ): String {
        videoService.save(videoService.getVideoById(videoId).get().apply {
            calibrationPointList = calibrationPointListWrapper.toCalibrationPointList()
        })

        backendBrokerService.computeCalibrationMatrix(
            activeBackendWebSocketSession!!,
            videoId,
            calibrationPointListWrapper.toCalibrationPointList()
        )

        return "redirect:/"
    }

    @PostMapping("video/start")
    fun startVideoStream() : String {
        backendBrokerService.startProcessingVideo(activeBackendWebSocketSession!!)

        return "redirect:/"
    }
}