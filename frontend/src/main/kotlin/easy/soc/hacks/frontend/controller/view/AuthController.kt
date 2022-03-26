package easy.soc.hacks.frontend.controller.view

import easy.soc.hacks.frontend.service.UserService
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.context.event.ApplicationReadyEvent
import org.springframework.context.event.EventListener
import org.springframework.stereotype.Controller
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestParam
import javax.servlet.http.HttpSession

@Controller
class AuthController {
    @Autowired
    private lateinit var userService: UserService

    @EventListener(ApplicationReadyEvent::class)
    fun ensureAdminExists() {
        val adminUser = userService.getAdmin()

        if (adminUser.isEmpty) {
            userService.saveAdmin()
        }
    }

    @GetMapping("login")
    fun getLogin(): String {
        return "login"
    }

    @PostMapping("login")
    fun postLogin(
        @RequestParam(name = "login") login: String,
        @RequestParam(name = "password") password: String,
        httpSession: HttpSession
    ): String {
        val user = userService.login(login, password).orElseGet { null }

        httpSession.setAttribute("user", user)

        return "redirect:/"
    }

    @GetMapping("logout")
    fun getLogout(httpSession: HttpSession): String {
        httpSession.removeAttribute("user")

        return "redirect:/"
    }
}