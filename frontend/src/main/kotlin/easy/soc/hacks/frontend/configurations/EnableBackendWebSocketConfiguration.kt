package easy.soc.hacks.frontend.configurations

import easy.soc.hacks.frontend.components.BackendWebSocketHandlerComponent
import org.springframework.context.annotation.Configuration
import org.springframework.web.socket.config.annotation.EnableWebSocket
import org.springframework.web.socket.config.annotation.WebSocketConfigurer
import org.springframework.web.socket.config.annotation.WebSocketHandlerRegistry

@Configuration
@EnableWebSocket
class EnableBackendWebSocketConfiguration : WebSocketConfigurer {
    override fun registerWebSocketHandlers(registry: WebSocketHandlerRegistry) {
        registry.addHandler(BackendWebSocketHandlerComponent(), "/backend/websocket")
    }
}