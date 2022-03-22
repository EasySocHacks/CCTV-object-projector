package easy.soc.hacks.frontend.service

import easy.soc.hacks.frontend.domain.CalibrationPoint
import easy.soc.hacks.frontend.domain.CameraVideo
import easy.soc.hacks.frontend.service.BackendBrokerService.Companion.Command.*
import org.json.JSONArray
import org.json.JSONObject
import org.springframework.stereotype.Service
import org.springframework.web.socket.TextMessage
import org.springframework.web.socket.WebSocketSession

@Service
class BackendBrokerService {
    companion object {
        enum class Command(
            private val text: String
        ) {
            APPEND_CAMERA_VIDEO("APPEND_CAMERA_VIDEO"),
            COMPUTE_CALIBRATION_MATRIX("COMPUTE_CALIBRATION_MATRIX"),
            START_PROCESSING_VIDEO("START_PROCESSING_VIDEO");

            override fun toString(): String = text
        }
    }

    fun appendCameraVideo(webSocketSession: WebSocketSession, cameraVideo: CameraVideo) {
        val json = JSONObject()
        json.put("command", APPEND_CAMERA_VIDEO.toString())
        json.put("url", cameraVideo.url)
        json.put("id", cameraVideo.id)
        webSocketSession.sendMessage(TextMessage(json.toString()))
    }

    fun computeCalibrationMatrix(webSocketSession: WebSocketSession, videoId: Long, calibrationPointList: List<CalibrationPoint>) {
        val json = JSONObject()
        json.put("command", COMPUTE_CALIBRATION_MATRIX.toString())
        json.put("videoId", videoId)
        val calibrationPointJsonArray = JSONArray()

        for (calibrationPoint in calibrationPointList) {
            val calibrationPointJson = JSONObject()
            calibrationPointJson.put("id", calibrationPoint.id)
            calibrationPointJson.put("xScreen", calibrationPoint.xScreen)
            calibrationPointJson.put("yScreen", calibrationPoint.yScreen)
            calibrationPointJson.put("xWorld", calibrationPoint.xWorld)
            calibrationPointJson.put("yWorld", calibrationPoint.yWorld)
            calibrationPointJson.put("zWorld", calibrationPoint.zWorld)

            calibrationPointJsonArray.put(calibrationPointJson)
        }

        json.put("calibrationPointList", calibrationPointJsonArray)
        webSocketSession.sendMessage(TextMessage(json.toString()))
    }

    fun startProcessingVideo(webSocketSession: WebSocketSession) {
        val json = JSONObject()
        json.put("command", START_PROCESSING_VIDEO.toString())

        webSocketSession.sendMessage(TextMessage(json.toString()))
    }
}