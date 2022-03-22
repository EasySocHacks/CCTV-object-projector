package easy.soc.hacks.frontend.services

import easy.soc.hacks.frontend.domains.Video
import easy.soc.hacks.frontend.repositories.VideoRepository
import easy.soc.hacks.frontend.services.VideoService.Companion.VideoStatus.STOP
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