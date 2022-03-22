package easy.soc.hacks.frontend.service

import easy.soc.hacks.frontend.domain.Video
import easy.soc.hacks.frontend.repository.VideoRepository
import easy.soc.hacks.frontend.service.VideoService.Companion.VideoStatus.STOP
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Service

@Service
class VideoService {
    companion object {
        enum class VideoStatus {
            START,
            STOP
        }

        var videoStatus = STOP
    }

    @Autowired
    private lateinit var videoRepository: VideoRepository

    fun getVideoById(id: Long) = videoRepository.getVideoById(id)

    fun findAll(): List<Video> = videoRepository.findAll()

    fun save(video: Video) = videoRepository.save(video)
}