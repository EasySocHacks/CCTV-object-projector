package easy.soc.hacks.frontend.interceptor

import org.springframework.http.HttpStatus.NOT_FOUND
import org.springframework.stereotype.Component
import org.springframework.web.servlet.HandlerInterceptor
import org.springframework.web.servlet.ModelAndView
import org.springframework.web.servlet.resource.ResourceHttpRequestHandler
import javax.servlet.http.HttpServletRequest
import javax.servlet.http.HttpServletResponse

@Component
class WebInterceptor : HandlerInterceptor {

    override fun preHandle(request: HttpServletRequest, response: HttpServletResponse, handler: Any): Boolean {
        val user = request.session.getAttribute("user")


        if (user == null && handler !is ResourceHttpRequestHandler && request.requestURI != "/login") {
            response.sendRedirect("/login")
            return false
        }

        if (user != null && request.requestURI == "/login") {
            response.sendRedirect("/")
            return false
        }

        if (response.status == NOT_FOUND.value()) {
            response.sendRedirect("/404")
            return false
        }

        return true
    }

    override fun postHandle(
        request: HttpServletRequest,
        response: HttpServletResponse,
        handler: Any,
        modelAndView: ModelAndView?
    ) {
        val user = request.session.getAttribute("user")
        modelAndView?.model?.put("user", user)
    }
}