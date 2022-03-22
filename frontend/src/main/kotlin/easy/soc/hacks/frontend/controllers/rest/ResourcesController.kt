package easy.soc.hacks.frontend.controllers.rest

import org.springframework.beans.factory.annotation.Autowired
import org.springframework.core.io.ResourceLoader
import org.springframework.http.HttpStatus.NOT_FOUND
import org.springframework.http.ResponseEntity
import org.springframework.stereotype.Controller
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestMapping

@Controller
@RequestMapping("api/v1")
class ResourcesController {
    @Autowired
    private lateinit var resourceLoader: ResourceLoader

    @GetMapping("resources/gif/loading")
    fun getLoadingGif(): ResponseEntity<ByteArray> {
        val resource = resourceLoader.getResource("media/gif/loading.gif")

        return if (resource.exists()) {
            ResponseEntity.ok().body(resource.file.readBytes())
        } else {
            ResponseEntity.status(NOT_FOUND).build()
        }
    }
}