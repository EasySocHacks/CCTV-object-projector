package easy.soc.hacks.frontend.service

import easy.soc.hacks.frontend.domain.CameraVideo
import org.json.JSONObject
import org.springframework.stereotype.Service
import org.springframework.web.socket.TextMessage
import org.springframework.web.socket.WebSocketSession

@Service
class BackendBrokerService {
    companion object {
        enum class Command(
            val text: String
        ) {
            APPEND_CAMERA_VIDEO("APPEND_CAMERA_VIDEO")
        }
    }

    fun appendCameraVideo(webSocketSession: WebSocketSession, cameraVideo: CameraVideo) {
        val json = JSONObject()
        json.put("command", Command.APPEND_CAMERA_VIDEO.text)
        json.put("url", cameraVideo.url)
        json.put("id", cameraVideo.id)
        webSocketSession.sendMessage(TextMessage(json.toString()))
    }
}