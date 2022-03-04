package easy.soc.hacks.frontend.controllers.view

import org.springframework.stereotype.Controller
import org.springframework.web.bind.annotation.GetMapping

@Controller
class ErrorController {
    @GetMapping("404")
    fun notFount(): String {
        return "404"
    }
}