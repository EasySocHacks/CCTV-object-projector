package easy.soc.hacks.frontend.services

import easy.soc.hacks.frontend.domains.VideoScreenshot
import easy.soc.hacks.frontend.repositories.VideoScreenshotRepository
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Service

@Service
class VideoScreenshotService {
    @Autowired
    private lateinit var videoScreenshotRepository: VideoScreenshotRepository

    fun save(videoScreenshot: VideoScreenshot) = videoScreenshotRepository.save(videoScreenshot)

    fun getVideoScreenshotByVideoId(videoId: Long) = videoScreenshotRepository.findById(videoId)
}