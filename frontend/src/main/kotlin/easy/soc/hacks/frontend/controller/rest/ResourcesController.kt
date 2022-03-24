package easy.soc.hacks.frontend.controller.rest

import org.springframework.http.HttpStatus.NOT_FOUND
import org.springframework.http.ResponseEntity
import org.springframework.stereotype.Controller
import org.springframework.util.ResourceUtils
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestMapping

@Controller
@RequestMapping("api/v1")
class ResourcesController {
    @GetMapping("resources/gif/loading")
    fun getLoadingGif(): ResponseEntity<ByteArray> {
        val resource = ResourceUtils.getFile("classpath:media/gif/loading.gif")

        return if (resource.exists()) {
            ResponseEntity.ok().body(resource.readBytes())
        } else {
            ResponseEntity.status(NOT_FOUND).build()
        }
    }
}