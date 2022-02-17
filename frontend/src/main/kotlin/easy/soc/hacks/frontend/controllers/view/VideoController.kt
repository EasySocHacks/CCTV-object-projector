package easy.soc.hacks.frontend.controllers.view

import easy.soc.hacks.frontend.controllers.rest.StreamingController.Companion.videoFragmentStreamServices
import easy.soc.hacks.frontend.domain.CameraVideo
import easy.soc.hacks.frontend.service.VideoFragmentStreamService
import org.springframework.stereotype.Controller
import org.springframework.ui.Model
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.ModelAttribute
import org.springframework.web.bind.annotation.PostMapping

@Controller
class VideoController {
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
        // TODO: ?: smth
        cameraVideo.id = videoFragmentStreamServices.keys.maxOrNull()?.plus(1)

        videoFragmentStreamServices[cameraVideo.id!!] = VideoFragmentStreamService(cameraVideo)

        return "redirect:/"
    }
}