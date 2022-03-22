package easy.soc.hacks.frontend.controllers.view

import easy.soc.hacks.frontend.components.BackendWebSocketHandlerComponent.Companion.activeBackendWebSocketSession
import easy.soc.hacks.frontend.domains.CalibrationPointListWrapper
import easy.soc.hacks.frontend.domains.CameraVideo
import easy.soc.hacks.frontend.services.BackendBrokerService
import easy.soc.hacks.frontend.services.CalibrationPointService
import easy.soc.hacks.frontend.services.VideoService
import easy.soc.hacks.frontend.services.VideoService.Companion.videoStatus
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
    private lateinit var videoService: VideoService

    @Autowired
    private lateinit var calibrationPointService: CalibrationPointService

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
        val savedVideo = videoService.save(cameraVideo) as CameraVideo
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
        // TODO: Change CameraVideo to Video inheritance
        with(videoService.getVideoById(videoId).get() as CameraVideo) {
            videoService.save(
                CameraVideo(
                    id = id,
                    name = name,
                    calibrationPointList = calibrationPointListWrapper.toCalibrationPointList().map {
                        calibrationPointService.save(it)
                    },
                    url = url
                )
            )
        }

        backendBrokerService.computeCalibrationMatrix(
            activeBackendWebSocketSession!!,
            videoId,
            calibrationPointListWrapper.toCalibrationPointList()
        )

        return "redirect:/"
    }

    @PostMapping("video/start")
    fun startVideoStream(): String {
        backendBrokerService.startProcessingVideo(activeBackendWebSocketSession!!)

        return "redirect:/"
    }
}