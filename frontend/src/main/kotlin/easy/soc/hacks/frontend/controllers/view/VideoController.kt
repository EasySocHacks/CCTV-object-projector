package easy.soc.hacks.frontend.controllers.view

import easy.soc.hacks.frontend.component.BackendWebSocketHandlerComponent.Companion.activeBackendWebSocketSession
import easy.soc.hacks.frontend.controllers.rest.StreamingController.Companion.videoFragmentStreamServices
import easy.soc.hacks.frontend.domain.CameraVideo
import easy.soc.hacks.frontend.service.BackendBrokerService
import easy.soc.hacks.frontend.service.VideoFragmentStreamService
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Controller
import org.springframework.ui.Model
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.ModelAttribute
import org.springframework.web.bind.annotation.PostMapping

@Controller
class VideoController {
    @Autowired
    private lateinit var backendBrokerService: BackendBrokerService

    @GetMapping("", "video/list/preview")
    fun previewVideoList(model: Model): String {
        model.addAttribute("streamServices", videoFragmentStreamServices)

        return "index"
    }

    @GetMapping("video/add")
    fun addVideo(): String {
        return "addVideo"
    }

    @PostMapping("video/add")
    fun addVideoToList(@ModelAttribute cameraVideo: CameraVideo): String {
        cameraVideo.id = videoFragmentStreamServices.keys.maxOrNull()?.plus(1) ?: 0

        if (activeBackendWebSocketSession != null) {
            videoFragmentStreamServices[cameraVideo.id!!] = VideoFragmentStreamService(cameraVideo)

            backendBrokerService.appendCameraVideo(activeBackendWebSocketSession!!, cameraVideo)
        } else {
            // TODO: Error message notification
        }

        return "redirect:/"
    }
}