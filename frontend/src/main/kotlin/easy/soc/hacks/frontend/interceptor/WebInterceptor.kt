package easy.soc.hacks.frontend.interceptor

import org.springframework.http.HttpStatus.NOT_FOUND
import org.springframework.web.servlet.HandlerInterceptor
import javax.servlet.http.HttpServletRequest
import javax.servlet.http.HttpServletResponse

class WebInterceptor : HandlerInterceptor {

    override fun preHandle(request: HttpServletRequest, response: HttpServletResponse, handler: Any): Boolean {
        if (response.status == NOT_FOUND.value()) {
            response.sendRedirect("/404")
        }

        return true
    }
}