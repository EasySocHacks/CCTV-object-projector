package easy.soc.hacks.frontend.service

import easy.soc.hacks.frontend.domain.VideoScreenshot
import easy.soc.hacks.frontend.repository.VideoScreenshotRepository
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Service

@Service
class VideoScreenshotService {
    @Autowired
    private lateinit var videoScreenshotRepository: VideoScreenshotRepository

    fun save(videoScreenshot: VideoScreenshot) = videoScreenshotRepository.save(videoScreenshot)

    fun getVideoScreenshotByVideoId(videoId: Long) = videoScreenshotRepository.findById(videoId)
}