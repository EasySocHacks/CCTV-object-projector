package easy.soc.hacks.frontend.components

import org.springframework.stereotype.Component
import org.springframework.web.socket.CloseStatus
import org.springframework.web.socket.WebSocketHandler
import org.springframework.web.socket.WebSocketMessage
import org.springframework.web.socket.WebSocketSession

@Component
class BackendWebSocketHandlerComponent : WebSocketHandler {
    companion object {
        var activeBackendWebSocketSession: WebSocketSession? = null
    }

    // TODO: logger
    override fun afterConnectionEstablished(session: WebSocketSession) {
        if (activeBackendWebSocketSession != null) {
            session.close(CloseStatus.NOT_ACCEPTABLE)
            return
        }
        activeBackendWebSocketSession = session
    }

    // TODO: do smth with response
    override fun handleMessage(session: WebSocketSession, message: WebSocketMessage<*>) {
        return
    }

    // TODO: throw custom exception
    override fun handleTransportError(session: WebSocketSession, exception: Throwable) {
        return
    }

    // TODO: logger
    override fun afterConnectionClosed(session: WebSocketSession, closeStatus: CloseStatus) {
        if (activeBackendWebSocketSession == session) {
            activeBackendWebSocketSession = null
        }
    }

    override fun supportsPartialMessages(): Boolean = false
}