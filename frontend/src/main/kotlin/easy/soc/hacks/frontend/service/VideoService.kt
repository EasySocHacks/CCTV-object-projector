package easy.soc.hacks.frontend.service

import easy.soc.hacks.frontend.domain.Video
import easy.soc.hacks.frontend.repository.VideoRepository
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Service

@Service
class VideoService {
    @Autowired
    private lateinit var videoRepository: VideoRepository

    fun getVideoById(id: Long) = videoRepository.getVideoById(id)

    fun findAll(): List<Video> = videoRepository.findAll()

    fun save(video: Video) = videoRepository.save(video)
}