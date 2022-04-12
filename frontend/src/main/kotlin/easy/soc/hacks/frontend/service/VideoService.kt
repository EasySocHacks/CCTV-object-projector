package easy.soc.hacks.frontend.service

import easy.soc.hacks.frontend.domain.Video
import easy.soc.hacks.frontend.repository.VideoRepository
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Service

@Service
class VideoService {
    @Autowired
    private lateinit var videoRepository: VideoRepository

    fun findVideoByIdAndSessionId(id: Long, sessionId: String) =
        videoRepository.findVideoByIdAndSessionId(id, sessionId)

    fun save(video: Video): Video {
        val id = videoRepository.save(
            video.session.id,
            video.name,
            video.streamingType.name,
            video.uri,
            video.data
        )

        return Video(
            id = id,
            session = video.session,
            name = video.name,
            uri = video.uri,
            calibrationPointList = video.calibrationPointList,
            streamingType = video.streamingType
        )
    }

    fun setCalibration(video: Video) {
        for (calibrationPoint in video.calibrationPointList) {
            videoRepository.setCalibration(
                video.id,
                video.session.id,
                calibrationPoint.id
            )
        }
    }

    fun findVideosBySessionId(sessionId: String) = videoRepository.findVideosBySessionId(sessionId)
}